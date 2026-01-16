#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch calendar page and extract all event IDs for January 2026
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

def get_calendar_events():
    """Fetch calendar page and extract event IDs by date"""
    
    print("=" * 60)
    print("📅 Vugraph Calendar Event Extractor")
    print("=" * 60)
    print("\n🌐 Fetching calendar page...")
    
    try:
        url = "https://clubs.vugraph.com/hosgoru/calendar.php"
        response = requests.get(url, timeout=15)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get all links with event IDs
        event_links = soup.find_all('a', href=re.compile(r'event=\d+'))
        
        events_by_date = {}
        
        print(f"✅ Found {len(event_links)} event links\n")
        
        for link in event_links:
            href = link.get('href', '')
            text = link.get_text().strip()
            
            # Extract event ID
            event_match = re.search(r'event=(\d+)', href)
            if not event_match:
                continue
            
            event_id = event_match.group(1)
            
            # Try to extract date from link text or nearby content
            # Format might be like "04.01.2026" or "4 Ocak"
            date_pattern = r'(\d{1,2})\.(\d{1,2})\.(\d{4})'
            date_match = re.search(date_pattern, text)
            
            if date_match:
                day = date_match.group(1).zfill(2)
                month = date_match.group(2).zfill(2)
                year = date_match.group(3)
                date_key = f"{year}-{month}-{day}"
                
                if date_key not in events_by_date:
                    events_by_date[date_key] = []
                
                events_by_date[date_key].append({
                    'event_id': event_id,
                    'text': text,
                    'url': href
                })
                
                print(f"📌 {date_key}: Event {event_id} - {text}")
        
        return events_by_date
    
    except Exception as e:
        print(f"❌ Error fetching calendar: {e}")
        return {}

def extract_events_for_january():
    """Get all events for January 2026"""
    
    events_by_date = get_calendar_events()
    
    if not events_by_date:
        print("\n⚠️  No events found on calendar")
        return None
    
    # Filter for January 2026
    january_events = {k: v for k, v in events_by_date.items() if k.startswith('2026-01')}
    
    print(f"\n{'=' * 60}")
    print(f"📋 January 2026 Events Summary:")
    print(f"{'=' * 60}")
    
    if january_events:
        for date_key in sorted(january_events.keys()):
            events = january_events[date_key]
            print(f"\n📅 {date_key}:")
            for event in events:
                print(f"   • Event {event['event_id']}: {event['text']}")
    else:
        print("⚠️  No events found for January 2026")
    
    return january_events

def main():
    events = extract_events_for_january()
    
    if events:
        # Prepare for fetching
        print(f"\n{'=' * 60}")
        print("🚀 Ready to fetch boards from these events")
        print(f"{'=' * 60}\n")
        
        # Show event IDs that need to be fetched
        event_ids = set()
        for date_key, event_list in events.items():
            for event in event_list:
                event_ids.add(event['event_id'])
        
        print(f"Event IDs to fetch: {', '.join(sorted(event_ids))}")
        print(f"\n💾 To fetch boards, you can use:")
        print(f"   python fetch_vugraph_hands.py")
        print(f"   Then enter event IDs when prompted (comma-separated)")

if __name__ == '__main__':
    main()
