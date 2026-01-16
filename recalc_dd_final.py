#!/usr/bin/env python3
"""
Recalculate Double Dummy analysis using pydd library
"""

import json
import sys

# Install and import pydd
try:
    from pydd import dds
    print("✓ pydd library found")
except ImportError:
    print("Installing pydd library...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "pydd"])
    from pydd import dds
    print("✓ pydd library installed")

# Load database
print("\nLoading database...")
with open("app/www/hands_database.json", "r", encoding="utf-8") as f:
    db = json.load(f)

# Get board data
boards = db['events']['hosgoru_04_01_2026']['boards']
print(f"Found {len(boards)} boards\n")

# Process each board
updated_count = 0

for board_num in sorted(boards.keys(), key=lambda x: int(x)):
    board_data = boards[board_num]
    hands = board_data.get('hands')
    
    if not hands:
        continue
    
    print(f"Board {board_num}...", end=" ", flush=True)
    
    try:
        # Extract hands
        n_hand = hands.get('North', {})
        s_hand = hands.get('South', {})
        e_hand = hands.get('East', {})
        w_hand = hands.get('West', {})
        
        # Create PBN string format
        # Format: N:S..H..D..C. W:S..H..D..C. E:S..H..D..C. S:S..H..D..C.
        pbn = (
            f"N:{n_hand.get('S', '')}.{n_hand.get('H', '')}.{n_hand.get('D', '')}.{n_hand.get('C', '')} "
            f"E:{e_hand.get('S', '')}.{e_hand.get('H', '')}.{e_hand.get('D', '')}.{e_hand.get('C', '')} "
            f"S:{s_hand.get('S', '')}.{s_hand.get('H', '')}.{s_hand.get('D', '')}.{s_hand.get('C', '')} "
            f"W:{w_hand.get('S', '')}.{w_hand.get('H', '')}.{w_hand.get('D', '')}.{w_hand.get('C', '')}"
        )
        
        # Solve
        table = dds.solve_board(pbn, -1)
        
        # Extract tricks for each suit and player
        dd_solution = {
            'NT': {'N': 0, 'E': 0, 'S': 0, 'W': 0},
            'S': {'N': 0, 'E': 0, 'S': 0, 'W': 0},
            'H': {'N': 0, 'E': 0, 'S': 0, 'W': 0},
            'D': {'N': 0, 'E': 0, 'S': 0, 'W': 0},
            'C': {'N': 0, 'E': 0, 'S': 0, 'W': 0}
        }
        
        # Map results
        suits = ['S', 'H', 'D', 'C', 'NT']
        players = ['N', 'E', 'S', 'W']
        
        for suit_idx, suit_name in enumerate(suits):
            for player_idx, player_name in enumerate(players):
                dd_solution[suit_name][player_name] = int(table[suit_idx][player_idx])
        
        board_data['dd_analysis'] = dd_solution
        updated_count += 1
        print("✓")
        
    except Exception as e:
        print(f"✗ Error: {str(e)[:50]}")
        continue

print(f"\n✓ Updated {updated_count}/{len(boards)} boards")

# Save database
print("\nSaving database...")
with open("app/www/hands_database.json", "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print("✓ Database saved!")
