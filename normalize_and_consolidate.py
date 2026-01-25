#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Normalize all event_ids to integers and remove duplicates"""

import json

data = json.load(open('hands_database.json', encoding='utf-8'))

print(f"Original database: {len(data)} hands\n")

# Normalize event_ids to integers
for hand in data:
    eid = hand.get('event_id')
    if isinstance(eid, str):
        hand['event_id'] = int(eid)
    elif isinstance(eid, int):
        pass  # Already int
    else:
        print(f"WARNING: Unexpected event_id type: {type(eid)}")

# Now remove duplicates using composite key
seen_keys = set()
cleaned_db = []
removed_count = 0

for hand in data:
    event_id = hand.get('event_id')
    board = hand.get('board')
    key = (event_id, board)
    
    if key not in seen_keys:
        seen_keys.add(key)
        cleaned_db.append(hand)
    else:
        removed_count += 1

print(f"Removed {removed_count} duplicates (after normalizing event_ids)")
print(f"Final database: {len(cleaned_db)} hands\n")

# Count per event
events_count = {}
for h in cleaned_db:
    eid = h.get('event_id')
    if eid not in events_count:
        events_count[eid] = 0
    events_count[eid] += 1

print(f"Events and hand counts:")
all_ok = True
for eid in sorted(events_count.keys()):
    count = events_count[eid]
    marker = "✓" if count == 30 else "✗"
    print(f"  Event {eid}: {count} hands {marker}")
    if count != 30:
        all_ok = False

# Save cleaned database
with open('hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(cleaned_db, f, ensure_ascii=False, indent=2)

print(f"\n✅ Database saved: {len(cleaned_db)} hands")
if all_ok and len(cleaned_db) == 690:
    print(f"✅ PERFECT: 23 events × 30 hands = 690 total hands")
else:
    print(f"⚠️ Total: {len(cleaned_db)} hands, Expected: 690")
