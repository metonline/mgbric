#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate 16 realistic bridge hands for 2026 tournaments (01.01 - 16.01)
Each hand properly distributed to N/S/E/W seats
"""

import json
import random

def generate_realistic_hand():
    """Generate a single realistic bridge hand"""
    suits = ['S', 'H', 'D', 'C']
    cards = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    
    # Create deck
    deck = []
    for suit in suits:
        for card in cards:
            deck.append(suit + card)
    
    # Shuffle and deal
    random.shuffle(deck)
    
    # Deal 13 cards to each player (N, S, E, W)
    positions = ['N', 'S', 'E', 'W']
    hand = {}
    
    for i, pos in enumerate(positions):
        player_cards = deck[i*13:(i+1)*13]
        hand[pos] = {
            'S': ''.join(sorted([c[1] for c in player_cards if c[0] == 'S'], 
                          key=lambda x: '23456789TJQKA'.index(x), reverse=True)),
            'H': ''.join(sorted([c[1] for c in player_cards if c[0] == 'H'], 
                          key=lambda x: '23456789TJQKA'.index(x), reverse=True)),
            'D': ''.join(sorted([c[1] for c in player_cards if c[0] == 'D'], 
                          key=lambda x: '23456789TJQKA'.index(x), reverse=True)),
            'C': ''.join(sorted([c[1] for c in player_cards if c[0] == 'C'], 
                          key=lambda x: '23456789TJQKA'.index(x), reverse=True))
        }
    
    return hand

def main():
    print("🎴 Generating 16 realistic bridge hands for 2026 tournaments\n")
    
    # Generate 16 boards (one per day, 01.01 - 16.01.2026)
    hands_db = {}
    dealers = ['N', 'E', 'S', 'W']
    vulnerabilities = ['None', 'NS', 'EW', 'Both']
    
    for board_num in range(1, 17):
        # Cycle through dealers and vulnerabilities for realism
        dealer = dealers[(board_num - 1) % 4]
        vuln = vulnerabilities[(board_num - 1) % 4]
        
        hand = generate_realistic_hand()
        
        hands_db[str(board_num)] = {
            'N': hand['N'],
            'S': hand['S'],
            'E': hand['E'],
            'W': hand['W'],
            'dealer': dealer,
            'vulnerability': vuln
        }
        
        print(f"Board {board_num:2d}: {dealer} deals, {vuln:6s} | N: {hand['N']['S']}{hand['N']['H']}{hand['N']['D']}{hand['N']['C']}")
    
    # Save to hands_database.json
    output_file = 'hands_database.json'
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(hands_db, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Generated {len(hands_db)} boards in {output_file}")
        print("\n📋 Sample board structure:")
        sample = hands_db['1']
        print(f"   N (North):  S:{sample['N']['S']} H:{sample['N']['H']} D:{sample['N']['D']} C:{sample['N']['C']}")
        print(f"   S (South):  S:{sample['S']['S']} H:{sample['S']['H']} D:{sample['S']['D']} C:{sample['S']['C']}")
        print(f"   E (East):   S:{sample['E']['S']} H:{sample['E']['H']} D:{sample['E']['D']} C:{sample['E']['C']}")
        print(f"   W (West):   S:{sample['W']['S']} H:{sample['W']['H']} D:{sample['W']['D']} C:{sample['W']['C']}")
        print(f"   Dealer: {sample['dealer']}")
        print(f"   Vuln: {sample['vulnerability']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()
