#!/usr/bin/env python3
"""
Calculate DD (Double Dummy) values locally using pydd
"""

import json
from pydd.dds import solve, Card

def hand_string_to_cards(s, h, d, c):
    """Convert hand notation to card list for pydd"""
    suits = [s, h, d, c]  # Spades, Hearts, Diamonds, Clubs
    cards = []
    suit_order = ['S', 'H', 'D', 'C']
    
    for suit_idx, suit_cards in enumerate(suits):
        suit_name = suit_order[suit_idx]
        for card_char in suit_cards:
            # Convert notation: 2-9, T=10, J, Q, K, A
            if card_char == 'T':
                rank = 10
            elif card_char == 'J':
                rank = 11
            elif card_char == 'Q':
                rank = 12
            elif card_char == 'K':
                rank = 13
            elif card_char == 'A':
                rank = 14
            else:
                rank = int(card_char)
            
            cards.append(Card(suit_name, rank))
    
    return cards

with open('app/www/hands_database.json', encoding='utf-8') as f:
    db = json.load(f)

boards = db['events']['hosgoru_04_01_2026']['boards']

print("Calculating DD values for all 30 boards...")
print("=" * 70)

results = {}

for board_num in range(1, 31):
    board = boards[str(board_num)]
    
    n_hand = board['hands']['North']
    e_hand = board['hands']['East']
    s_hand = board['hands']['South']
    w_hand = board['hands']['West']
    
    try:
        # Get cards for each hand
        n_cards = hand_string_to_cards(n_hand['S'], n_hand['H'], n_hand['D'], n_hand['C'])
        e_cards = hand_string_to_cards(e_hand['S'], e_hand['H'], e_hand['D'], e_hand['C'])
        s_cards = hand_string_to_cards(s_hand['S'], s_hand['H'], s_hand['D'], s_hand['C'])
        w_cards = hand_string_to_cards(w_hand['S'], w_hand['H'], w_hand['D'], w_hand['C'])
        
        # Calculate DD table
        # solve expects hands in order: N, E, S, W
        table = solve([n_cards, e_cards, s_cards, w_cards], 0, 0)
        
        print(f"Board {board_num}: ✓")
        
        # Store results
        results[board_num] = {
            'N': list(table[0]),  # Tricks for N in each strain
            'E': list(table[1]),  # Tricks for E
            'S': list(table[2]),  # Tricks for S
            'W': list(table[3])   # Tricks for W
        }
        
    except Exception as e:
        print(f"Board {board_num}: ✗ Error - {str(e)}")

print("=" * 70)
print(f"Successfully calculated DD values for {len(results)} boards")

if results:
    # Save to file for review
    with open('dd_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("✓ Results saved to dd_results.json")
    
    # Show sample
    print(f"\nSample - Board 1:")
    print(f"  Strains: NT, Spades, Hearts, Diamonds, Clubs")
    if 1 in results:
        print(f"  N tricks: {results[1]['N']}")
        print(f"  E tricks: {results[1]['E']}")
        print(f"  S tricks: {results[1]['S']}")
        print(f"  W tricks: {results[1]['W']}")
