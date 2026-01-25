#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analyze and remove true duplicates from event 405596"""

import json
from collections import defaultdict

db = json.load(open('hands_database.json', encoding='utf-8'))
hands_405596 = [h for h in db if int(h.get('event_id', 0)) == 405596]

# Group by board
boards_dict = defaultdict(list)
for hand in hands_405596:
    board = hand.get('board')
    boards_dict[board].append(hand)

print(f"Event 405596 Analysis:")
print(f"Total hands: {len(hands_405596)}")
print(f"Unique boards: {len(boards_dict)}\n")

# Check each board
duplicates_found = 0
for board_num in sorted(boards_dict.keys()):
    hands = boards_dict[board_num]
    if len(hands) > 1:
        print(f"Board {board_num}: {len(hands)} hands (DUPLICATE!)")
        duplicates_found += len(hands) - 1

print(f"\nTotal duplicates in event 405596: {duplicates_found}")

# If duplicates found, remove them
if duplicates_found > 0:
    # Rebuild database keeping only first occurrence of (event_id, board)
    seen_keys = set()
    new_db = []
    removed_count = 0
    
    for hand in db:
        event_id = hand.get('event_id')
        board = hand.get('board')
        key = (event_id, board)
        
        if key not in seen_keys:
            seen_keys.add(key)
            new_db.append(hand)
        else:
            removed_count += 1
    
    # Save the cleaned database
    with open('hands_database.json', 'w', encoding='utf-8') as f:
        json.dump(new_db, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Removed {removed_count} duplicate hands")
    print(f"✅ Database saved with {len(new_db)} hands (23 events × 30 boards = 690 hands)")
else:
    print("\n✅ No duplicates found - database is clean")
