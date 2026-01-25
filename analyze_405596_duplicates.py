#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check why event 405596 has 60 hands instead of 30"""

import json
from collections import defaultdict

db = json.load(open('hands_database.json'))
hands_405596 = [h for h in db if int(h.get('event_id', 0)) == 405596]

# Group by board
boards = defaultdict(list)
for hand in hands_405596:
    boards[hand.get('board')].append(hand)

print(f"Total hands from event 405596: {len(hands_405596)}")
print(f"Boards: {sorted(boards.keys())}\n")

# Find boards with duplicates
duplicated_boards = {b: hands for b, hands in boards.items() if len(hands) > 1}
print(f"Boards with duplicates: {len(duplicated_boards)}")

if duplicated_boards:
    print("\nAnalyzing first duplicated board:")
    board_num = sorted(duplicated_boards.keys())[0]
    hands = duplicated_boards[board_num]
    
    print(f"\nBoard {board_num}: {len(hands)} hands")
    
    h1, h2 = hands[0], hands[1]
    
    # Check if all fields are identical
    keys_to_check = ['N', 'E', 'S', 'W', 'dealer', 'date', 'lin_string', 'dd_analysis', 'optimum', 'lott']
    
    for key in keys_to_check:
        val1 = h1.get(key)
        val2 = h2.get(key)
        if val1 != val2:
            print(f"  {key}: DIFFERENT")
            if len(str(val1)) < 100 and len(str(val2)) < 100:
                print(f"    Hand 1: {val1}")
                print(f"    Hand 2: {val2}")
            else:
                print(f"    Hand 1: {str(val1)[:80]}...")
                print(f"    Hand 2: {str(val2)[:80]}...")
        else:
            print(f"  {key}: SAME")
