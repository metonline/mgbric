#!/usr/bin/env python3
"""
Extract hands from LIN file - parse 3 hands and calculate the 4th from 52-card deck
"""
import json
import re
from collections import defaultdict

def parse_lin_hands(md_string):
    """
    Parse MD line from LIN file
    Format: md|N:spades,hearts,diamonds,clubs|E:...|S:...
    Returns dict with N, E, S, W hands in PBN format
    """
    if not md_string or not md_string.startswith('md|'):
        return None
    
    try:
        # Parse the MD string: md|N:spades,hearts,diamonds,clubs|E:...|S:...
        parts = md_string[3:].split('|')  # Remove 'md|' and split
        hands = {}
        
        for part in parts:
            if ':' not in part:
                continue
            direction, cards_str = part.split(':', 1)
            if direction not in ['N', 'E', 'S']:
                continue
            suits = cards_str.split(',')
            if len(suits) == 4:
                # Format as PBN: S.H.D.C
                hand_pbn = f"{suits[0]}.{suits[1]}.{suits[2]}.{suits[3]}"
                hands[direction] = hand_pbn
        
        if 'N' not in hands or 'E' not in hands or 'S' not in hands:
            return None
        
        # Calculate W from remaining cards in 52-card deck
        all_suits = {
            'S': list('AKQJT98765432'),
            'H': list('AKQJT98765432'),
            'D': list('AKQJT98765432'),
            'C': list('AKQJT98765432'),
        }
        
        # Remove cards from N, E, S
        suit_names = ['S', 'H', 'D', 'C']
        for direction in ['N', 'E', 'S']:
            hand = hands[direction]
            suits_in_hand = hand.split('.')
            for suit_idx, cards in enumerate(suits_in_hand):
                suit = suit_names[suit_idx]
                for card in cards:
                    if card in all_suits[suit]:
                        all_suits[suit].remove(card)
        
        # W gets the remaining cards
        w_hand = f"{(''.join(all_suits['S']) or '-')}.{(''.join(all_suits['H']) or '-')}.{(''.join(all_suits['D']) or '-')}.{(''.join(all_suits['C']) or '-')}"
        hands['W'] = w_hand
        
        return hands
    except Exception as e:
        print(f"Error parsing: {md_string} - {e}")
        return None

# Read LIN file
print("Extracting hands from event_405376.lin...")
hands_data = []
board_num = 0
date = "20.01.2026"
event_id = "405376"

with open('event_405376.lin', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        
        # Find md field
        md_match = re.search(r'md\|[^|]*(?:\|[^|]*)*', line)
        if md_match:
            board_num += 1
            if board_num > 30:
                break
            
            md_field = md_match.group()
            
            # Calculate dealer based on board number
            dealer_cycle = (board_num - 1) % 4
            dealers = ['N', 'E', 'S', 'W']
            dealer = dealers[dealer_cycle]
            
            hands = parse_lin_hands(md_field)
            if hands:
                hand_obj = {
                    'id': 405376 * 100 + board_num,
                    'event_id': event_id,
                    'board': board_num,
                    'date': date,
                    'dealer': dealer,
                    'vulnerability': 'None',
                    'N': hands['N'],
                    'E': hands['E'],
                    'S': hands['S'],
                    'W': hands['W'],
                    'dd_analysis': {},
                    'optimum': {},
                    'lott': {}
                }
                hands_data.append(hand_obj)
                if board_num <= 3:
                    print(f"  Board {board_num}: N={hands['N'][:15]} E={hands['E'][:15]}")

print(f"\n✓ Extracted {len(hands_data)} hands from LIN file")

# Load current database and replace these hands
with open('hands_database.json', 'r', encoding='utf-8') as f:
    all_hands = json.load(f)

# Replace hands for 20.01.2026 event 405376
all_hands = [h for h in all_hands if not (h['date'] == date and h['event_id'] == event_id)]
all_hands.extend(hands_data)

# Sort by date and board
all_hands.sort(key=lambda x: (x['date'], x['board']))

# Save
with open('hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(all_hands, f, ensure_ascii=False, indent=2)

print(f"✓ Saved {len(all_hands)} total hands to hands_database.json")

# Verify
h = [x for x in all_hands if x['date']=='20.01.2026' and x['board']==1]
if h:
    h = h[0]
    print()
    print("Board 1 - 20.01.2026 verification:")
    print(f"N: {h['N']}")
    print(f"E: {h['E']}")
    print(f"S: {h['S']}")
    print(f"W: {h['W']}")
