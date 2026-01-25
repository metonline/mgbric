#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug why duplicates aren't being removed"""

import json

db = json.load(open('hands_database.json', encoding='utf-8'))

# Find the first instance of event 405596, board 1
seen_keys = set()
new_db = []
removed_count = 0
debug = False

for idx, hand in enumerate(db):
    event_id = hand.get('event_id')
    board = hand.get('board')
    key = (event_id, board)
    
    # Debug event 405596
    if event_id == 405596 and board == 1:
        debug = True
        print(f"Index {idx}: Event {event_id}, Board {board}")
        print(f"  Key: {key}")
        print(f"  Key in seen_keys: {key in seen_keys}")
    
    if key not in seen_keys:
        seen_keys.add(key)
        new_db.append(hand)
        if debug:
            print(f"  -> ADDED to new_db")
    else:
        removed_count += 1
        if debug:
            print(f"  -> SKIPPED (duplicate)")
    
    if debug and board == 1 and event_id == 405596:
        debug = False

print(f"\nTotal hands before: {len(db)}")
print(f"Total hands after: {len(new_db)}")
print(f"Removed: {removed_count}")

# Check event 405596 in new database
hands_405596 = [h for h in new_db if h.get('event_id') == 405596]
print(f"\nEvent 405596 in cleaned database: {len(hands_405596)} hands")

if removed_count > 0:
    # Save
    with open('hands_database.json', 'w', encoding='utf-8') as f:
        json.dump(new_db, f, ensure_ascii=False, indent=2)
    print(f"✅ Database saved!")
