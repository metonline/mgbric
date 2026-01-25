#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FINAL: Remove ALL duplicates using (event_id, board) composite key"""

import json

db = json.load(open('hands_database.json', encoding='utf-8'))

print(f"Starting with: {len(db)} hands\n")

# Use composite key: (event_id, board)
seen_keys = set()
cleaned_db = []
removed = []

for hand in db:
    event_id = hand.get('event_id')
    board = hand.get('board')
    key = (event_id, board)
    
    if key not in seen_keys:
        seen_keys.add(key)
        cleaned_db.append(hand)
    else:
        removed.append((event_id, board))

print(f"Removed {len(removed)} duplicates using composite key (event_id, board)")

if removed:
    print(f"\nDuplicates found and removed:")
    from collections import Counter
    removed_by_event = Counter(e for e, b in removed)
    for event_id in sorted(removed_by_event.keys()):
        count = removed_by_event[event_id]
        print(f"  Event {event_id}: {count} duplicate hands")

# Verify
events = {}
for h in cleaned_db:
    eid = int(h.get('event_id', 0)) if h.get('event_id') else 0
    if eid not in events:
        events[eid] = 0
    events[eid] += 1

print(f"\nVerification:")
print(f"  Total hands: {len(cleaned_db)}")
print(f"  Total events: {len(events)}")
print(f"  Expected: 23 events × 30 hands = 690")

# Save FINAL database
with open('hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(cleaned_db, f, ensure_ascii=False, indent=2)

print(f"\n✅ CONSOLIDATED: hands_database.json saved with {len(cleaned_db)} hands")

# Show per-event breakdown
all_ok = True
for eid in sorted(events.keys()):
    count = events[eid]
    if count != 30:
        print(f"  ⚠️ Event {eid}: {count} hands (expected 30)")
        all_ok = False

if all_ok and len(cleaned_db) == 690:
    print(f"✅ ALL EVENTS HAVE EXACTLY 30 HANDS - DATABASE IS CLEAN!")
