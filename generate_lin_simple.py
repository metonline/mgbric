#!/usr/bin/env python3
"""
Generate tournament_boards.lin from the fetched hands database.
This LIN file can be used with Bridge Solver Online.
"""

import json
import os

def create_lin_file():
    """Create LIN file from hands database"""
    
    # Load the fetched hands database
    db_path = 'app/www/hands_database.json'
    
    if not os.path.exists(db_path):
        print(f"Error: {db_path} not found")
        return False
    
    with open(db_path, 'r', encoding='utf-8') as f:
        boards = json.load(f)
    
    print(f"Loaded {len(boards)} boards from {db_path}")
    
    # Generate LIN format for each board
    lin_lines = []
    
    for board_num in sorted([int(b) for b in boards.keys()]):
        board_str = str(board_num)
        hands = boards[board_str]
        
        # Extract hands in the right format
        # LIN format: dealer, vulnerability, and hands in format: W hand,N hand,E hand
        # For simplicity, assume: dealer rotates (board N: dealer = (N-1) mod 4), No vuln
        
        dealers = ['N', 'E', 'S', 'W']
        dealer = dealers[(board_num - 1) % 4]
        
        # Build hand strings: Sx, Hx, Dx, Cx for each player
        def build_hand_string(hand_dict):
            parts = []
            for suit in ['S', 'H', 'D', 'C']:
                cards = hand_dict.get(suit, '')
                if cards:
                    parts.append(cards)
                else:
                    parts.append('-')
            return '.'.join(parts)
        
        # Get hands - LIN format expects: W,N,E (South is dealer/dummy)
        w_hand = build_hand_string(hands['W'])
        n_hand = build_hand_string(hands['N'])
        e_hand = build_hand_string(hands['E'])
        s_hand = build_hand_string(hands['S'])
        
        # Create LIN entry
        # Format: st||bn=N,dips1=W,dips2=N,dips3=E,dips4=S||
        # Or simpler format for Bridge Solver
        
        # Using simplified format:
        lin_entry = f"qb||"  # Start board definition
        lin_entry += f"bn={board_num}|"  # Board number
        lin_entry += f"d={dealer}|"  # Dealer
        lin_entry += f"v=none|"  # Vulnerability
        lin_entry += f"w={w_hand}|"  # West hand
        lin_entry += f"n={n_hand}|"  # North hand
        lin_entry += f"e={e_hand}|"  # East hand
        lin_entry += f"s={s_hand}|"  # South hand
        
        lin_lines.append(lin_entry)
    
    # Write LIN file
    output_path = 'app/www/tournament_boards.lin'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in lin_lines:
            f.write(line + '\n')
    
    print(f"\n✅ Generated {len(lin_lines)} boards in {output_path}")
    
    # Show sample
    if lin_lines:
        print(f"\nSample (Board 1):\n{lin_lines[0][:100]}...")
    
    return True

if __name__ == '__main__':
    create_lin_file()
