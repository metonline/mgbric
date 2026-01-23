#!/usr/bin/env python3
"""Event için el verilerini çeker ve hands_database.json'a ekler"""

import requests
from bs4 import BeautifulSoup
import json
import re
import sys

def fetch_hands_for_event(event_id, date):
    """Bir event için tüm board'ların el verilerini çeker"""
    hands = []
    
    for board_num in range(1, 31):
        url = f'https://clubs.vugraph.com/hosgoru/board.php?p=&id={event_id}&b={board_num}'
        try:
            response = requests.get(url, timeout=30)
            response.encoding = 'iso-8859-9'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # El verisi - LIN formatında
            lin_tag = soup.find('input', {'id': 'lindata'})
            if lin_tag and lin_tag.get('value'):
                lin_data = lin_tag['value']
                # LIN formatından elleri parse et: md|1S.H.D.C,E's hand,S's hand|
                md_match = re.search(r'md\|([0-9])([^|]+)\|', lin_data)
                if md_match:
                    dealer_idx = int(md_match.group(1))
                    hands_str = md_match.group(2)
                    # Parse hands
                    hand_parts = hands_str.split(',')
                    if len(hand_parts) >= 3:
                        # Dealer'a göre sıra: 1=N, 2=E, 3=S, 4=W
                        dealer_map = {1: 'N', 2: 'E', 3: 'S', 4: 'W'}
                        dealer = dealer_map[dealer_idx]
                        
                        hand_data = {
                            'event_id': str(event_id),
                            'Tarih': date,
                            'Board': board_num,
                            'N': '', 'S': '', 'E': '', 'W': '',
                            'Dealer': dealer,
                            'Vuln': ''
                        }
                        
                        # İlk el dealer'ın eli
                        positions = ['N', 'E', 'S', 'W']
                        start_idx = positions.index(dealer)
                        for i, part in enumerate(hand_parts[:4]):
                            pos = positions[(start_idx + i) % 4]
                            hand_data[pos] = part
                        
                        hands.append(hand_data)
                        n_preview = hand_data['N'][:15] if hand_data['N'] else 'empty'
                        print(f"  Board {board_num}: OK ({n_preview})")
                    else:
                        print(f"  Board {board_num}: Parse error - not enough parts")
                else:
                    print(f"  Board {board_num}: No md pattern found")
            else:
                print(f"  Board {board_num}: No LIN data")
        except Exception as e:
            print(f"  Board {board_num}: Error - {str(e)[:40]}")
    
    return hands

def main():
    event_id = sys.argv[1] if len(sys.argv) > 1 else '405376'
    date = sys.argv[2] if len(sys.argv) > 2 else '20.01.2026'
    
    print(f'Fetching hands for event {event_id} ({date})...')
    hands = fetch_hands_for_event(event_id, date)
    print(f'\nFetched {len(hands)} hands')
    
    if hands:
        # hands_database.json'a ekle
        with open('hands_database.json', 'r', encoding='utf-8') as f:
            db = json.load(f)
        
        # Mevcut event_id + Board kombinasyonlarını bul
        existing = {(str(h.get('event_id', '')), h.get('Board')) for h in db}
        
        new_hands = [h for h in hands if (h['event_id'], h['Board']) not in existing]
        if new_hands:
            db.extend(new_hands)
            with open('hands_database.json', 'w', encoding='utf-8') as f:
                json.dump(db, f, indent=2, ensure_ascii=False)
            print(f'Added {len(new_hands)} new hands to database')
        else:
            print('All hands already exist')

if __name__ == '__main__':
    main()
