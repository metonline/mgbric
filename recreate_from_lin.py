#!/usr/bin/env python3
"""
Recreate hands_database.json from the LIN file.
The LIN file has the correct hand data.
"""

import json
import re

def parse_lin_line(line, board_num):
    """Parse a single LIN line and extract hands"""
    # Format: qx|o1|md|{dealer}{west},{north},{east}|rh||ah|Board N|sv|{vuln}|pg||
    
    # Extract relevant parts
    match = re.search(r'md\|(\d)([^|]+)\|', line)
    if not match:
        return None
    
    dealer_pos = int(match.group(1))
    hands_str = match.group(2)
    
    # Dealer map: 1=N, 2=E, 3=S, 4=W
    dealer_map = {1: 'N', 2: 'E', 3: 'S', 4: 'W'}
    dealer = dealer_map[dealer_pos]
    
    # Parse hands (West, North, East format in LIN)
    hands_parts = hands_str.split(',')
    if len(hands_parts) < 3:
        return None
    
    west_lin, north_lin, east_lin = hands_parts[0], hands_parts[1], hands_parts[2]
    
    # Extract vulnerability from line
    vuln_match = re.search(r'sv\|(\d)\|', line)
    vuln_code = int(vuln_match.group(1)) if vuln_match else 0
    vuln_map = {0: 'None', 1: 'N-S', 2: 'E-W', 3: 'Both'}
    vulnerability = vuln_map[vuln_code]
    
    # Parse LIN hand format: Suit + cards (no separators)
    def parse_hand_lin(hand_str):
        """Parse hand from LIN format: SAKJ2H52DA8CAQT62"""
        hand = {}
        current_suit = None
        current_cards = ""
        
        for char in hand_str:
            if char in 'SHDC':
                if current_suit:
                    hand[current_suit] = current_cards
                current_suit = char
                current_cards = ""
            else:
                current_cards += char
        
        if current_suit:
            hand[current_suit] = current_cards
        
        return hand
    
    west_hand = parse_hand_lin(west_lin)
    north_hand = parse_hand_lin(north_lin)
    east_hand = parse_hand_lin(east_lin)
    
    # Compute South hand from remaining cards
    # All suits have: A, K, Q, J, T, 9, 8, 7, 6, 5, 4, 3, 2 (13 cards each)
    suit_all_cards = '23456789TJQKA'  # Standard order (reversed for easier matching)
    
    south_hand = {}
    for suit in ['S', 'H', 'D', 'C']:
        # Get cards held by North, East, West in this suit
        held_cards = (north_hand.get(suit, '') + 
                     east_hand.get(suit, '') + 
                     west_hand.get(suit, ''))
        
        # South gets the remaining cards
        south_cards = ''.join(c for c in suit_all_cards if c not in held_cards)
        south_hand[suit] = south_cards
    
    return {
        'dealer': dealer,
        'vulnerability': vulnerability,
        'North': north_hand,
        'South': south_hand,
        'East': east_hand,
        'West': west_hand
    }

# Read LIN file
with open('app/www/tournament_boards.lin', 'r', encoding='utf-8') as f:
    lin_lines = f.readlines()

# Create database structure
db = {
    "events": {
        "hosgoru_04_01_2026": {
            "name": "Hoşgörü Pazar Simultane",
            "date": "04.01.2026",
            "location": "Istanbul",
            "section": "A",
            "boards": {}
        }
    }
}

# Parse each LIN line
print("="*70)
print("RECREATING HANDS DATABASE FROM LIN FILE")
print("="*70)

for board_num, lin_line in enumerate(lin_lines, 1):
    lin_line = lin_line.strip()
    if not lin_line:
        continue
    
    board_data = parse_lin_line(lin_line, board_num)
    if not board_data:
        print(f"✗ Board {board_num}: Failed to parse")
        continue
    
    db["events"]["hosgoru_04_01_2026"]["boards"][str(board_num)] = {
        "dealer": board_data['dealer'],
        "vulnerability": board_data['vulnerability'],
        "hands": {
            "North": board_data['North'],
            "South": board_data['South'],
            "East": board_data['East'],
            "West": board_data['West']
        },
        "dd_analysis": {},
        "results": [],
        "doubleVDummy": {
            "table": {},
            "par": "TBD",
            "date_generated": "2026-01-06"
        }
    }
    
    print(f"✅ Board {board_num}: {board_data['dealer']} dealer, {board_data['vulnerability']}")

# Save
with open('app/www/hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print("\n" + "="*70)
print(f"✅ Recreated hands_database.json from LIN file")
print(f"✅ Total boards: {len(db['events']['hosgoru_04_01_2026']['boards'])}")
print("="*70)

# Verify first 3 boards
print("\n✅ Verification - Board 1:")
b1 = db["events"]["hosgoru_04_01_2026"]["boards"]["1"]
for player in ['North', 'South', 'East', 'West']:
    hand = b1['hands'][player]
    suits = ' '.join([f'{s}{hand.get(s, "")}' for s in ['S', 'H', 'D', 'C']])
    print(f"  {player:6}: {suits}")
