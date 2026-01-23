#!/usr/bin/env python3
"""
Calculate DD (Double Dummy) values using DDS library
"""

import json
import dds

def parse_hand(s, h, d, c):
    """Parse hand string to DDS format"""
    # DDS expects: 52-card representation
    # We need to convert from notation to DDS card format
    
    suits_str = [s, h, d, c]  # S, H, D, C
    
    # Each suit represented as bitmask
    suit_masks = [0, 0, 0, 0]
    
    for suit_idx, cards_str in enumerate(suits_str):
        mask = 0
        for card_char in cards_str:
            # Convert card to rank (2-14, where A=14, K=13, Q=12, J=11, T=10)
            if card_char == 'A':
                rank = 14
            elif card_char == 'K':
                rank = 13
            elif card_char == 'Q':
                rank = 12
            elif card_char == 'J':
                rank = 11
            elif card_char == 'T':
                rank = 10
            else:
                rank = int(card_char)
            
            # Add bit for this rank (bit 2 = 2, bit 14 = A)
            mask |= (1 << rank)
        
        suit_masks[suit_idx] = mask
    
    return suit_masks

with open('app/www/hands_database.json', encoding='utf-8') as f:
    db = json.load(f)

boards = db['events']['hosgoru_04_01_2026']['boards']

print("Calculating DD values for all 30 boards...")
print("=" * 70)

dd_results = {}
success_count = 0

for board_num in range(1, 31):
    board = boards[str(board_num)]
    
    try:
        n_hand = board['hands']['North']
        e_hand = board['hands']['East']
        s_hand = board['hands']['South']
        w_hand = board['hands']['West']
        
        # Parse each hand to DDS format
        n_suits = parse_hand(n_hand['S'], n_hand['H'], n_hand['D'], n_hand['C'])
        e_suits = parse_hand(e_hand['S'], e_hand['H'], e_hand['D'], e_hand['C'])
        s_suits = parse_hand(s_hand['S'], s_hand['H'], s_hand['D'], s_hand['C'])
        w_suits = parse_hand(w_hand['S'], w_hand['H'], w_hand['D'], w_hand['C'])
        
        # Create hands array for DDS (N, E, S, W)
        hands = [n_suits, e_suits, s_suits, w_suits]
        
        # Calculate DD for all suits and all players
        # DDS solves: tricks available for declarers in each strain
        # The function returns tricks for: NT, Spades, Hearts, Diamonds, Clubs for each player
        
        table = dds.calc_all_tables(hands)
        
        dd_results[board_num] = table
        print(f"Board {board_num}: ✓")
        success_count += 1
        
    except Exception as e:
        print(f"Board {board_num}: ✗ Error - {str(e)[:50]}")

print("=" * 70)
print(f"Successfully calculated DD values for {success_count}/30 boards")

if success_count > 0:
    # Save raw results
    with open('dd_results_raw.json', 'w') as f:
        # Convert to serializable format
        serializable = {}
        for board_num, result in dd_results.items():
            serializable[str(board_num)] = result
        json.dump(serializable, f, indent=2)
    
    print("✓ Results saved to dd_results_raw.json")
    print("\nNote: Results need to be formatted for database update.")
