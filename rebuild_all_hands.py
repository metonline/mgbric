#!/usr/bin/env python3
"""
REBUILD ALL HANDS DATABASE FROM SCRATCH
Fetches hands for all events since 1.1.2026 and calculates DD/LoTT

Usage: python rebuild_all_hands.py
"""

import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

# Configuration
ALL_CARDS = 'AKQJT98765432'

def validate_hand(hand_str):
    """Validate hand format: S.H.D.C with valid cards"""
    if not hand_str or hand_str.count('.') != 3:
        return False
    suits = hand_str.split('.')
    return all(c in ALL_CARDS or c == '' for suit in suits for c in suit)

def count_cards(hand_str):
    """Count total cards in hand"""
    if not hand_str:
        return 0
    return sum(len(suit) for suit in hand_str.split('.'))

def calc_4th_hand(h1, h2, h3):
    """Calculate 4th hand from remaining cards"""
    result = []
    for suit_idx in range(4):
        s1 = h1.split('.')[suit_idx] if h1 else ''
        s2 = h2.split('.')[suit_idx] if h2 else ''
        s3 = h3.split('.')[suit_idx] if h3 else ''
        used = s1 + s2 + s3
        remaining = ''.join(c for c in ALL_CARDS if c not in used)
        result.append(remaining)
    return '.'.join(result)

def get_dealer(board_num):
    """Get dealer for board number (1-based cycle)"""
    return ['N', 'E', 'S', 'W'][(board_num - 1) % 4]

def get_vulnerability(board_num):
    """Get vulnerability for board number"""
    cycle = (board_num - 1) % 16
    if cycle in [0, 7, 10, 13]:
        return 'None'
    elif cycle in [1, 4, 11, 14]:
        return 'NS'
    elif cycle in [2, 5, 8, 15]:
        return 'EW'
    else:
        return 'Both'

def fetch_hands_for_event(event_id, date):
    """Fetch all hands for an event from vugraph"""
    hands = []
    print(f"\n{'='*60}")
    print(f"Fetching event {event_id} ({date})")
    print('='*60)
    
    for board_num in range(1, 31):
        url = f'https://clubs.vugraph.com/hosgoru/board.php?p=&id={event_id}&b={board_num}'
        try:
            response = requests.get(url, timeout=30)
            response.encoding = 'iso-8859-9'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get LIN data
            lin_tag = soup.find('input', {'id': 'lindata'})
            if not lin_tag or not lin_tag.get('value'):
                print(f"  Board {board_num}: No LIN data")
                continue
            
            lin_data = lin_tag['value']
            
            # Parse md|dealer hands|
            md_match = re.search(r'md\|(\d)([^|]+)\|', lin_data)
            if not md_match:
                print(f"  Board {board_num}: No md pattern")
                continue
            
            dealer_num = int(md_match.group(1))
            hands_str = md_match.group(2)
            hand_parts = hands_str.split(',')
            
            if len(hand_parts) < 3:
                print(f"  Board {board_num}: Not enough hands")
                continue
            
            # Dealer mapping
            dealer_map = {1: 'N', 2: 'E', 3: 'S', 4: 'W'}
            dealer = dealer_map[dealer_num]
            
            # Rotate hands to N-E-S-W
            positions = ['N', 'E', 'S', 'W']
            start_idx = positions.index(dealer)
            
            nesw = {}
            for i, part in enumerate(hand_parts[:3]):
                pos = positions[(start_idx + i) % 4]
                nesw[pos] = part
            
            # Calculate 4th hand
            given = list(nesw.values())
            missing_pos = [p for p in positions if p not in nesw][0]
            nesw[missing_pos] = calc_4th_hand(given[0], given[1], given[2])
            
            # Validate
            total_cards = sum(count_cards(nesw[p]) for p in positions)
            if total_cards != 52:
                print(f"  Board {board_num}: Card count {total_cards} != 52")
                continue
            
            # Create hand entry
            hand_data = {
                'event_id': str(event_id),
                'board': board_num,
                'date': date,
                'dealer': dealer,
                'vulnerability': get_vulnerability(board_num),
                'hands': {
                    'N': nesw['N'],
                    'E': nesw['E'],
                    'S': nesw['S'],
                    'W': nesw['W']
                }
            }
            hands.append(hand_data)
            print(f"  Board {board_num}: ✓ N={nesw['N'][:12]}...")
            
        except Exception as e:
            print(f"  Board {board_num}: Error - {str(e)[:40]}")
    
    print(f"\n✓ Fetched {len(hands)}/30 hands for event {event_id}")
    return hands

def main():
    print("="*60)
    print("REBUILD ALL HANDS DATABASE")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load events from database.json
    with open('database.json', 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    events = db.get('events', {})
    print(f"\nFound {len(events)} events in database.json")
    
    # Sort by date
    event_list = []
    for key, event in events.items():
        event_id = event.get('id', key.replace('event_', ''))
        date = event.get('date', '')
        event_list.append((event_id, date))
    
    event_list.sort(key=lambda x: x[1])
    print("Events to process:")
    for eid, date in event_list:
        print(f"  - {eid}: {date}")
    
    # Fetch hands for all events
    all_hands = []
    for event_id, date in event_list:
        hands = fetch_hands_for_event(event_id, date)
        all_hands.extend(hands)
    
    print(f"\n{'='*60}")
    print(f"TOTAL: {len(all_hands)} hands fetched")
    print('='*60)
    
    # Save to hands_database.json
    with open('hands_database.json', 'w', encoding='utf-8') as f:
        json.dump(all_hands, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved to hands_database.json")
    
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nNext step: Run DD solver with:")
    print("  python double_dummy/dd_solver.py --update-db")

if __name__ == '__main__':
    main()
