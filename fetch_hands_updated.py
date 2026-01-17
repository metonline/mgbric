#!/usr/bin/env python3
"""
Fetch tournament hands from Vugraph for dates 9.1 - 17.1.2026
Updates hands_database.json with new hands
"""

import json
import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime, timedelta

def get_tournaments_for_date_range():
    """Get all tournament IDs from database.json for date range"""
    try:
        with open('database.json', 'r', encoding='utf-8') as f:
            db = json.load(f)
    except:
        print("❌ Could not load database.json")
        return {}
    
    # Date range: January 9 to January 16, 2026 (latest available)
    start_date = datetime.strptime("09.01.2026", "%d.%m.%Y")
    end_date = datetime.strptime("16.01.2026", "%d.%m.%Y")
    
    tournaments = {}
    
    for record in db:
        try:
            tarih = record.get('Tarih', '')
            link = record.get('Link', '')
            turnuva = record.get('Turnuva', '')
            
            if not tarih or not link:
                continue
            
            # Extract event ID from link
            if 'event=' not in link:
                continue
            
            event_id = link.split('event=')[1].split('&')[0]
            
            # Parse date
            try:
                record_date = datetime.strptime(tarih, "%d.%m.%Y")
            except:
                continue
            
            if start_date <= record_date <= end_date:
                if event_id not in tournaments:
                    tournaments[event_id] = {
                        'date': tarih,
                        'name': turnuva,
                    }
        except:
            continue
    
    return tournaments

def parse_hand_from_html(html_text):
    """Extract hand deals from HTML"""
    soup = BeautifulSoup(html_text, 'html.parser')
    
    hands = {}
    
    try:
        # Find all player cells
        cells = soup.find_all('td', {'class': 'oyuncu'})
        
        for cell in cells:
            name_span = cell.find('span', {'class': 'isim'})
            if not name_span:
                continue
            
            hand_dict = {}
            html_str = str(cell)
            
            # Extract cards for each suit
            for suit_name, suit_symbol in [('spades', 'S'), ('hearts', 'H'), ('diamonds', 'D'), ('clubs', 'C')]:
                pattern = rf'<img[^>]*alt="{suit_name}"[^>]*/>[\s]*([A2-9TJKQX-]*)'
                match = re.search(pattern, html_str, re.IGNORECASE)
                
                if match:
                    cards = match.group(1).strip().upper()
                    hand_dict[suit_symbol] = cards if cards and cards != '-' else ''
            
            if len(hand_dict) == 4:
                if 'N' not in hands:
                    hands['N'] = hand_dict
                elif 'S' not in hands:
                    hands['S'] = hand_dict
                elif 'E' not in hands:
                    hands['E'] = hand_dict
                elif 'W' not in hands:
                    hands['W'] = hand_dict
    except:
        pass
    
    return hands if len(hands) == 4 else {}

def fetch_hands_for_event(event_id):
    """Fetch hands for an event"""
    base_url = "https://clubs.vugraph.com/hosgoru"
    hands_data = {}
    board_num = 1
    
    print(f"  📥 Fetching event {event_id}...", end='', flush=True)
    
    try:
        # Try fetching first 40 boards (typical tournament size)
        for board in range(1, 41):
            url = f"{base_url}/boardsummary.php?event={event_id}&board={board}"
            
            try:
                response = requests.get(url, timeout=5)
                response.encoding = 'utf-8'
                
                # Check if page exists
                if "Not Found" in response.text or response.status_code == 404:
                    break
                
                hands = parse_hand_from_html(response.text)
                if hands and len(hands) == 4:
                    hands_data[str(board)] = hands
                    print(".", end='', flush=True)
                
                time.sleep(0.2)  # Rate limiting
            except:
                continue
        
        print(f" ✓ ({len(hands_data)} boards)")
        return hands_data
    except Exception as e:
        print(f" ❌ Error: {e}")
        return {}

def main():
    print("\n" + "="*70)
    print("FETCH HANDS FROM VUGRAPH (9.1 - 17.1.2026)")
    print("="*70)
    
    # Load existing hands
    try:
        with open('hands_database.json', 'r', encoding='utf-8') as f:
            all_hands = json.load(f)
    except:
        all_hands = {}
    
    print(f"\n📊 Current hands in database: {len(all_hands)}")
    
    # Get tournaments for date range
    tournaments = get_tournaments_for_date_range()
    print(f"📅 Tournaments found for 9.1-17.1.2026: {len(tournaments)}")
    
    if not tournaments:
        print("❌ No tournaments found")
        return
    
    # Fetch hands for each tournament
    print(f"\n🔄 Fetching hands...")
    new_count = 0
    
    for idx, (event_id, info) in enumerate(sorted(tournaments.items()), 1):
        print(f"\n[{idx}/{len(tournaments)}] {event_id} ({info['date']})")
        
        hands = fetch_hands_for_event(event_id)
        
        if hands:
            # Add to database with unique keys
            for board_id, board_hands in hands.items():
                unique_id = str(len(all_hands) + 1)
                all_hands[unique_id] = board_hands
                new_count += 1
        
        time.sleep(0.5)
    
    # Save updated database
    print(f"\n💾 Saving updated database...")
    with open('hands_database.json', 'w', encoding='utf-8') as f:
        json.dump(all_hands, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ COMPLETE!")
    print(f"   Previous hands: {len(all_hands) - new_count}")
    print(f"   New hands: {new_count}")
    print(f"   Total hands: {len(all_hands)}")

if __name__ == '__main__':
    main()
