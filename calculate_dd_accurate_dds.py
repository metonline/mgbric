#!/usr/bin/env python3
"""
Calculate accurate Double Dummy analysis using DDS library
"""

import json
import dds

def calculate_dd_accurate(hand_data):
    """
    Calculate DD using DDS library - most accurate method
    """
    
    # Map card strings to DDS format
    def parse_hand(hand_dict):
        """Convert hand dict to DDS format (holdings)"""
        holdings = []
        for suit in ['S', 'H', 'D', 'C']:
            suit_str = hand_dict.get(suit, '')
            cards = []
            # Convert ranks to DDS format
            rank_map = {'2': 0, '3': 1, '4': 2, '5': 3, '6': 4, '7': 5, 
                       '8': 6, '9': 7, 'T': 8, 'J': 9, 'Q': 10, 'K': 11, 'A': 12}
            
            for card in suit_str:
                if card in rank_map:
                    cards.append(rank_map[card])
            
            # Sort in descending order for DDS
            holdings.append(sorted(cards, reverse=True))
        
        return holdings
    
    try:
        # Parse all four hands
        north_holdings = parse_hand(hand_data['N'])
        east_holdings = parse_hand(hand_data['E'])
        south_holdings = parse_hand(hand_data['S'])
        west_holdings = parse_hand(hand_data['W'])
        
        # Create DDS holdings structure
        holdings = [north_holdings, east_holdings, south_holdings, west_holdings]
        
        # Calculate DD table
        dd_table = dds.calc_dd_table(holdings)
        
        # Extract results
        # dd_table is a list of 4 lists of 5 values (for each player and denomination)
        # Denominations: 0=NT, 1=S, 2=H, 3=D, 4=C
        # Players: 0=N, 1=E, 2=S, 3=W
        
        result = {}
        denom_names = ['NT', 'S', 'H', 'D', 'C']
        player_names = ['N', 'E', 'S', 'W']
        
        for player_idx, player_name in enumerate(player_names):
            for denom_idx, denom_name in enumerate(denom_names):
                key = f"{denom_name}{player_name}"
                value = dd_table[player_idx][denom_idx]
                result[key] = value
        
        return result
    
    except Exception as e:
        print(f"Error calculating DD with DDS: {e}")
        return None

# Load database
print("Loading hands_database.json...")
with open('hands_database.json', 'r', encoding='utf-8') as f:
    hands = json.load(f)

# Calculate DD for all boards (including updating 101-110)
print("Calculating DD for all 110 boards using DDS library...")
updated_count = 0

for board_id in range(1, 111):
    board_key = str(board_id)
    if board_key in hands:
        board = hands[board_key]
        
        # Skip board 101 - we already have the correct values
        if board_id == 101:
            print(f"Board {board_id}: Skipped (already verified)")
            continue
        
        # Calculate DD
        dd_analysis = calculate_dd_accurate(board)
        if dd_analysis:
            board['dd_analysis'] = dd_analysis
            updated_count += 1
            if board_id <= 10 or board_id >= 101:
                print(f"Board {board_id}: OK")
            elif board_id % 10 == 0:
                print(f"Board {board_id}: OK")

# Save
print(f"\nSaving {updated_count} updated boards...")
with open('hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(hands, f, indent=2, ensure_ascii=False)

print(f"Done! Updated hands_database.json with accurate DDS calculations")
print(f"Total boards with DD analysis: {sum(1 for b in hands.values() if 'dd_analysis' in b and b['dd_analysis'])}")
