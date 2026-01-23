#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Normalize hands_database.json field names to match expected format:
- date (not Tarih)
- board (not Board)  
- dealer (not Dealer)
- vulnerability (not Vuln)
And add missing dealer/vulnerability based on board number
"""

import json

# Load hands database
with open('hands_database.json', 'r', encoding='utf-8') as f:
    hands = json.load(f)

def get_dealer_by_board(board_num):
    """Get dealer based on board number (standard bridge rotation)"""
    dealers = ['N', 'E', 'S', 'W']
    return dealers[(board_num - 1) % 4]

def get_vulnerability_by_board(board_num):
    """Get vulnerability based on board number (standard bridge rotation)"""
    # Standard 16-board vulnerability pattern
    vuln_pattern = [
        'None', 'NS', 'EW', 'Both',  # 1-4
        'NS', 'EW', 'Both', 'None',   # 5-8
        'EW', 'Both', 'None', 'NS',   # 9-12
        'Both', 'None', 'NS', 'EW'    # 13-16
    ]
    return vuln_pattern[(board_num - 1) % 16]

normalized_hands = []
for hand in hands:
    # Determine board number
    board = hand.get('board') or hand.get('Board')
    if board is None:
        continue
    board = int(board)
    
    # Determine date
    date = hand.get('date') or hand.get('Tarih') or 'Unknown'
    
    # Normalize to expected format
    normalized = {
        'id': hand.get('id') or len(normalized_hands) + 1,
        'board': board,
        'event_id': hand.get('event_id', ''),
        'event_name': hand.get('event_name', ''),
        'date': date,
        'direction': hand.get('direction', ''),
        'pair': hand.get('pair', ''),
        'score': hand.get('score', ''),
        'dealer': hand.get('dealer') or hand.get('Dealer') or get_dealer_by_board(board),
        'vulnerability': hand.get('vulnerability') or hand.get('Vuln') or get_vulnerability_by_board(board),
        'N': hand.get('N', ''),
        'S': hand.get('S', ''),
        'E': hand.get('E', ''),
        'W': hand.get('W', ''),
        'dd_analysis': hand.get('dd_analysis', {})
    }
    
    # Clean empty dealer/vulnerability
    if not normalized['dealer']:
        normalized['dealer'] = get_dealer_by_board(board)
    if not normalized['vulnerability']:
        normalized['vulnerability'] = get_vulnerability_by_board(board)
    
    normalized_hands.append(normalized)

# Sort by date and board
def sort_key(h):
    date = h.get('date', '01.01.2000')
    parts = date.split('.')
    if len(parts) == 3:
        return (int(parts[2]), int(parts[1]), int(parts[0]), h.get('board', 0))
    return (0, 0, 0, 0)

normalized_hands.sort(key=sort_key)

# Remove duplicates (keep first occurrence per date+board)
seen = set()
unique_hands = []
for hand in normalized_hands:
    key = f"{hand['date']}_{hand['board']}"
    if key not in seen:
        seen.add(key)
        unique_hands.append(hand)

# Save normalized database
with open('hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(unique_hands, f, indent=2, ensure_ascii=False)

print(f"Normalized {len(unique_hands)} hands")
print(f"\nSample hand:")
print(json.dumps(unique_hands[0], indent=2, ensure_ascii=False))
