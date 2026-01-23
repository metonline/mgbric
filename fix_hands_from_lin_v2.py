#!/usr/bin/env python3
"""
Extract hands from vugraph LIN file
LIN format: hands are ALWAYS listed as N, E, S (in that order)
W (West) is calculated from remaining 52 cards
"""
import json
import re

def calculate_fourth_hand(n_hand, e_hand, s_hand):
    """
    Calculate the 4th hand (W) from remaining 52 cards
    """
    # Map all 52 cards
    suits = ['S', 'H', 'D', 'C']
    ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
    
    all_cards = set()
    for suit in suits:
        for rank in ranks:
            all_cards.add(rank + suit)
    
    # Parse the 3 hands and remove their cards
    for hand_pbn in [n_hand, e_hand, s_hand]:
        parts = hand_pbn.split('.')
        for suit_idx, suit in enumerate(suits):
            cards = parts[suit_idx] if suit_idx < len(parts) else ''
            for card in cards:
                all_cards.discard(card + suit)
    
    # Organize remaining cards by suit
    remaining = {'S': '', 'H': '', 'D': '', 'C': ''}
    for card in sorted(all_cards, key=lambda x: (ranks.index(x[0]))):
        remaining[card[1]] += card[0]
    
    # Return in PBN format (S.H.D.C)
    return f"{remaining['S']}.{remaining['H']}.{remaining['D']}.{remaining['C']}"

# Parse LIN file
lin_file = 'event_405376.lin'
hands_from_lin = {}

with open(lin_file, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
            
        # Find md| section which contains hands
        # Format: md|1K86.QJT7.AQT.832,975.A53.KJ93.J76,T42.2.8542.KQT54|sv|
        md_match = re.search(r'md\|(\d+)(.*?)\|sv\|', line)
        if md_match:
            board_num = int(md_match.group(1))
            hands_str = md_match.group(2)
            
            # hands_str contains N,E,S in order
            hands_parts = hands_str.split(',')
            
            if len(hands_parts) >= 3:
                n_hand = hands_parts[0]
                e_hand = hands_parts[1]
                s_hand = hands_parts[2]
                
                # Calculate W from remaining cards
                w_hand = calculate_fourth_hand(n_hand, e_hand, s_hand)
                
                hands_from_lin[board_num] = {
                    'N': n_hand,
                    'E': e_hand,
                    'S': s_hand,
                    'W': w_hand
                }
                
                print(f"Board {board_num}:")
                print(f"  N: {n_hand}")
                print(f"  E: {e_hand}")
                print(f"  S: {s_hand}")
                print(f"  W: {w_hand} (calculated)")

print(f"\n✓ Extracted {len(hands_from_lin)} boards from LIN file")

# Load existing hands_database.json
with open('hands_database.json', 'r', encoding='utf-8') as f:
    all_hands = json.load(f)

print(f"✓ Loaded {len(all_hands)} hands from database")

# Update only event 405376 on 20.01.2026 with LIN data
fixed_count = 0
for hand in all_hands:
    if hand['event_id'] == '405376' and hand['date'] == '20.01.2026':
        board_num = hand['board']
        if board_num in hands_from_lin:
            lin_hand = hands_from_lin[board_num]
            hand['N'] = lin_hand['N']
            hand['E'] = lin_hand['E']
            hand['S'] = lin_hand['S']
            hand['W'] = lin_hand['W']
            fixed_count += 1

print(f"✓ Fixed {fixed_count} hands from event 405376 on 20.01.2026")

# Save corrected database
with open('hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(all_hands, f, ensure_ascii=False, indent=2)

print("✓ Saved hands_database.json")

# Verify
h = [x for x in all_hands if x['date']=='20.01.2026' and x['board']==1 and x['event_id']=='405376'][0]
print()
print("="*60)
print("Board 1 - 20.01.2026 verification:")
print(f"N: {h['N']}")
print(f"E: {h['E']}")
print(f"S: {h['S']}")
print(f"W: {h['W']}")
print()
print("Expected:")
print("N: K86.QJT7.AQT.832")
print("E: 975.A53.KJ93.J76")
print("S: T42.2.8542.KQT54")
print("W: AQJ3.K9864.76.A9")
print("="*60)
