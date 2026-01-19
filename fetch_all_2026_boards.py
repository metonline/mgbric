#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch all boards from 01.01.2026 to 17.01.2026 from Vugraph
and update hands_database.json with real card data
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
import sys
import io

# Set stdout encoding to UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Event ID'ler tarih bazında
EVENTS = {
    "01.01.2026": "404155",
    "02.01.2026": "404197",
    "03.01.2026": "404275",
    "04.01.2026": "404377",
    "05.01.2026": "404426",
    "06.01.2026": "404498",
    "07.01.2026": "404562",
    "08.01.2026": "404628",
    "09.01.2026": "404691",
    "10.01.2026": "404854",
    "11.01.2026": "404821",
    "12.01.2026": "404876",
    "13.01.2026": "405128",
    "14.01.2026": "405007",
    "15.01.2026": "405061",
    "16.01.2026": "405123",
    "17.01.2026": "405204",
    "18.01.2026": "405278",
}

BASE_URL = "https://clubs.vugraph.com/hosgoru/"

def extract_hands_from_page(html_content):
    """Extract hand information from Vugraph board detail page"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    hands = {
        'N': {'S': '', 'H': '', 'D': '', 'C': ''},
        'S': {'S': '', 'H': '', 'D': '', 'C': ''},
        'E': {'S': '', 'H': '', 'D': '', 'C': ''},
        'W': {'S': '', 'H': '', 'D': '', 'C': ''}
    }
    
    # Find the bridgetable which contains the hands
    bridge_table = soup.find('table', class_='bridgetable')
    if not bridge_table:
        return None
    
    # Get all cells with oyuncu class (player cells)
    player_cells = bridge_table.find_all('td', class_='oyuncu')
    
    if len(player_cells) < 4:
        return None
    
    # Extract from each player cell - order: West, North, East, South
    directions = ['W', 'N', 'E', 'S']
    
    for idx, cell in enumerate(player_cells):
        if idx >= 4:
            break
        
        direction = directions[idx]
        
        # Find all img tags with suit images
        suit_imgs = cell.find_all('img')
        
        # Extract suits and cards
        for img in suit_imgs:
            # Get the alt attribute to determine suit
            alt_text = img.get('alt', '').lower()
            
            suit = None
            if 'spade' in alt_text:
                suit = 'S'
            elif 'heart' in alt_text:
                suit = 'H'
            elif 'diamond' in alt_text:
                suit = 'D'
            elif 'club' in alt_text:
                suit = 'C'
            
            if not suit:
                continue
            
            # Get text immediately after the img tag
            next_elem = img.next_sibling
            cards = ''
            
            while next_elem:
                if isinstance(next_elem, str):
                    text = str(next_elem).strip()
                    if text and text != '<br />' and text != '-':
                        cards = text.replace('<br />', '').replace('\n', '').strip()
                        break
                    if text == '-':
                        cards = ''
                        break
                next_elem = next_elem.next_sibling
            
            if cards:
                hands[direction][suit] = cards
    
    return hands

def fetch_board_hands(event_id, board_num):
    """Fetch hand data for a specific board"""
    # Try different section/pair combinations
    for section in ['A', 'B']:
        for pair in range(1, 25):
            url = f"{BASE_URL}boarddetails.php?event={event_id}&section={section}&pair={pair}&direction=NS&board={board_num}"
            
            try:
                response = requests.get(url, timeout=10)
                response.encoding = 'utf-8'
                
                # Check if page loaded
                if response.status_code == 200 and 'bridgetable' in response.text:
                    hands = extract_hands_from_page(response.text)
                    if hands and any(h.get('S') or h.get('H') or h.get('D') or h.get('C') for h in hands.values()):
                        return hands
                
                time.sleep(0.05)
            except:
                continue
    
    return None

def format_hand_for_bbo(hands):
    """Convert extracted hands to BBO viewer format"""
    result = {}
    for direction in ['N', 'S', 'E', 'W']:
        spades = hands[direction].get('S', '')
        hearts = hands[direction].get('H', '')
        diamonds = hands[direction].get('D', '')
        clubs = hands[direction].get('C', '')
        # BBO format: SPADES.HEARTS.DIAMONDS.CLUBS
        result[direction] = f"{spades}.{hearts}.{diamonds}.{clubs}"
    return result

def main():
    print("\n" + "="*70)
    print("FETCHING ALL BOARDS FROM 01.01.2026 TO 17.01.2026")
    print("="*70 + "\n")
    
    # Load existing hands_database.json
    try:
        with open('hands_database.json', 'r', encoding='utf-8') as f:
            hands_db = json.load(f)
    except:
        hands_db = []
    
    # Create index by date and board
    hands_index = {}
    for hand in hands_db:
        key = f"{hand.get('Tarih', '')}_{hand.get('Board', '')}"
        hands_index[key] = hand
    
    total_updated = 0
    total_failed = 0
    
    # Process each date
    for tarih, event_id in EVENTS.items():
        print(f"\n{'='*50}")
        print(f"Processing {tarih} (Event: {event_id})")
        print("="*50)
        
        updated = 0
        failed = 0
        
        # Fetch boards 1-30
        for board_num in range(1, 31):
            key = f"{tarih}_{board_num}"
            
            # Check if already has real data
            if key in hands_index:
                existing = hands_index[key]
                north_hand = existing.get('N', '')
                if north_hand and north_hand != 'AKQJ.KQJ.AKQ.AKQ':
                    print(f"  Board {board_num:2d}: Already has real data, skipping")
                    continue
            
            print(f"  Board {board_num:2d}: Fetching...", end='', flush=True)
            
            hands = fetch_board_hands(event_id, board_num)
            
            if hands:
                bbo_hands = format_hand_for_bbo(hands)
                
                if key in hands_index:
                    # Update existing record
                    hands_index[key]['N'] = bbo_hands['N']
                    hands_index[key]['S'] = bbo_hands['S']
                    hands_index[key]['E'] = bbo_hands['E']
                    hands_index[key]['W'] = bbo_hands['W']
                else:
                    # Create new record
                    new_record = {
                        'Tarih': tarih,
                        'Board': board_num,
                        'N': bbo_hands['N'],
                        'S': bbo_hands['S'],
                        'E': bbo_hands['E'],
                        'W': bbo_hands['W'],
                        'Dealer': '',
                        'Vuln': ''
                    }
                    hands_db.append(new_record)
                    hands_index[key] = new_record
                
                print(f" OK - N: {bbo_hands['N'][:20]}...")
                updated += 1
            else:
                print(" FAILED")
                failed += 1
            
            time.sleep(0.1)
        
        total_updated += updated
        total_failed += failed
        print(f"\n  {tarih}: {updated} updated, {failed} failed")
    
    print(f"\n{'='*70}")
    print(f"TOTAL: {total_updated} boards updated, {total_failed} boards failed")
    print("="*70)
    
    # Rebuild hands_db from index
    hands_db = list(hands_index.values())
    
    # Sort by date and board
    def sort_key(h):
        tarih = h.get('Tarih', '01.01.2000')
        parts = tarih.split('.')
        if len(parts) == 3:
            return (int(parts[2]), int(parts[1]), int(parts[0]), h.get('Board', 0))
        return (0, 0, 0, 0)
    
    hands_db.sort(key=sort_key)
    
    # Save updated database
    with open('hands_database.json', 'w', encoding='utf-8') as f:
        json.dump(hands_db, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved to hands_database.json ({len(hands_db)} total hands)")

if __name__ == '__main__':
    main()
