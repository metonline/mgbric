#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch fresh tournament data from Vugraph
"""

import json
import requests
import sys
import os
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

DB_FILE = 'database.json'
BASE_URL = "https://clubs.vugraph.com/hosgoru"

def load_database():
    """Load database"""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Database yükleme hatası: {e}")
            return None
    return None

def save_database(db):
    """Save database"""
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Database kayıt hatası: {e}")
        return False

def fetch_calendar():
    """Get calendar page"""
    try:
        print("📅 Takvim getiriliyor...")
        response = requests.get(f"{BASE_URL}/calendar.php", timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"❌ Takvim hatası: {e}")
        return None

def parse_events_from_calendar(html):
    """Parse all events from calendar"""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        events = []
        
        # Find all event links
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            if 'eventresults.php?event=' in href:
                try:
                    event_id = href.split('event=')[1].split('&')[0]
                    events.append({
                        'event_id': event_id,
                        'name': text,
                        'url': href
                    })
                except:
                    pass
        
        return events
    except Exception as e:
        print(f"❌ Parse hatası: {e}")
        return []

def fetch_event_details(event_id):
    """Fetch details for a single event"""
    try:
        url = f"{BASE_URL}/eventresults.php?event={event_id}"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get event name from title or heading
        title = soup.find('h1') or soup.find('h2')
        event_name = title.get_text(strip=True) if title else f"Event {event_id}"
        
        # Extract tables (NS and EW sections)
        tables = soup.find_all('table', class_='colored')
        
        results = {
            'NS': [],
            'EW': []
        }
        
        for table in tables:
            rows = table.find_all('tr')
            current_direction = None
            
            for row in rows:
                # Check for section headers
                th = row.find('th')
                if th:
                    text = th.get_text(strip=True).upper()
                    if 'NORTH' in text or 'KUZEY' in text:
                        current_direction = 'NS'
                    elif 'EAST' in text or 'DOĞU' in text:
                        current_direction = 'EW'
                
                # Parse data rows
                tds = row.find_all('td')
                if len(tds) >= 4 and current_direction:
                    try:
                        rank = tds[0].get_text(strip=True)
                        if rank.isdigit():
                            pair_info = tds[1].get_text(strip=True)
                            score = tds[-1].get_text(strip=True)
                            
                            results[current_direction].append({
                                'rank': int(rank),
                                'pair': pair_info,
                                'score': score
                            })
                    except:
                        pass
        
        return {
            'event_id': event_id,
            'name': event_name,
            'date': datetime.now().isoformat(),
            'results': results
        }
    except Exception as e:
        print(f"❌ Event {event_id} hatası: {e}")
        return None

def update_database_with_events():
    """Fetch and update database with fresh data"""
    
    print("\n" + "="*60)
    print("🔄 VUGRAPH VERİ GÜNCELLEME")
    print("="*60)
    
    # Load database
    db = load_database()
    if not db:
        print("❌ Database bulunamadı!")
        return False
    
    # Fetch calendar
    calendar_html = fetch_calendar()
    if not calendar_html:
        print("❌ Takvim alınamadı!")
        return False
    
    # Parse events
    print("📊 Etkinlikler analiz ediliyor...")
    events = parse_events_from_calendar(calendar_html)
    print(f"   ✓ {len(events)} etkinlik bulundu")
    
    if not events:
        print("⚠️  Hiç etkinlik bulunamadı!")
        return False
    
    # Fetch details for each event (limit to 5 recent)
    for i, event_info in enumerate(events[:5]):
        event_id = event_info['event_id']
        print(f"\n📥 Event {i+1}/5: {event_id}")
        
        details = fetch_event_details(event_id)
        if details:
            # Use event_id as key
            db['events'][event_id] = details
            print(f"   ✓ Kaydedildi: {details['name']}")
            if details['results']['NS']:
                print(f"   ✓ NS: {len(details['results']['NS'])} çift")
            if details['results']['EW']:
                print(f"   ✓ EW: {len(details['results']['EW'])} çift")
    
    # Update metadata
    db['last_updated'] = datetime.now().isoformat()
    db['metadata']['total_tournaments'] = len(db['events'])
    
    # Save
    if save_database(db):
        print("\n" + "="*60)
        print("✅ VERİ GÜNCELLEME BAŞARILI")
        print("="*60)
        print(f"   📂 Toplam Etkinlik: {len(db['events'])}")
        print(f"   ⏰ Güncelleme: {db['last_updated']}")
        return True
    else:
        print("❌ Database kayıtlamada hata!")
        return False

if __name__ == '__main__':
    update_database_with_events()
