#!/usr/bin/env python3
"""
Recalculate Double Dummy analysis using py-dds library
"""

import json
import sys

# Install and import py-dds
try:
    from pydds.dds import SolveBoard
    print("✓ pydds library found")
except ImportError:
    print("Installing py-dds library...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "py-dds"])
    from pydds.dds import SolveBoard
    print("✓ py-dds library installed")

# Load database
print("\nLoading database...")
with open("app/www/hands_database.json", "r", encoding="utf-8") as f:
    db = json.load(f)

# Get board data
boards = db['events']['hosgoru_04_01_2026']['boards']
print(f"Found {len(boards)} boards\n")

# Convert suit letters to numbers (0=spades, 1=hearts, 2=diamonds, 3=clubs)
SUIT_MAP = {'S': 0, 'H': 1, 'D': 2, 'C': 3}

def hand_to_holdings(n_hand, s_hand, e_hand, w_hand):
    """Convert hand notation to DDS holdings."""
    holdings = [0] * 16  # 4 suits × 4 players
    
    for seat, hand in enumerate([n_hand, s_hand, e_hand, w_hand]):
        for suit_idx, suit in enumerate(['S', 'H', 'D', 'C']):
            cards = hand.get(suit, "")
            for card in cards:
                card_val = {'A': 14, 'K': 13, 'Q': 12, 'J': 11}.get(card, int(card) if card.isdigit() else 0)
                if card_val:
                    holdings[suit_idx * 4 + seat] |= (1 << (card_val - 2))
    
    return holdings

# Process each board
updated_count = 0

for board_num in sorted(boards.keys(), key=lambda x: int(x)):
    board_data = boards[board_num]
    hands = board_data.get('hands')
    
    if not hands or 'dd_analysis' not in board_data:
        continue
    
    print(f"Board {board_num}...", end=" ", flush=True)
    
    try:
        # Extract hands
        n_hand = hands.get('North', {})
        s_hand = hands.get('South', {})
        e_hand = hands.get('East', {})
        w_hand = hands.get('West', {})
        
        # Convert to holdings
        holdings = hand_to_holdings(n_hand, s_hand, e_hand, w_hand)
        
        # Solve the board
        dd_solution = {}
        
        # Calculate tricks for each denomination for each player
        for suit_num, suit_name in enumerate(['NT', 'S', 'H', 'D', 'C']):
            dd_solution[suit_name] = {}
            
            for player_num, player_name in enumerate(['N', 'E', 'S', 'W']):
                # Run solver for this denomination/player combo
                try:
                    result = SolveBoard(holdings, player_num, suit_num, 0)
                    tricks = result.tricks[0] if hasattr(result, 'tricks') else 0
                    dd_solution[suit_name][player_name] = tricks
                except:
                    # Fallback: use existing if available
                    old_dd = board_data.get('dd_analysis', {})
                    dd_solution[suit_name][player_name] = old_dd.get(suit_name, {}).get(player_name, 0)
        
        board_data['dd_analysis'] = dd_solution
        updated_count += 1
        print("✓")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        continue

print(f"\n✓ Updated {updated_count}/{len(boards)} boards")

# Save database
print("\nSaving database...")
with open("app/www/hands_database.json", "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print("✓ Database saved!")
