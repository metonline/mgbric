#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Remove duplicate hands using event_id and board as composite key"""

import json

db = json.load(open('hands_database.json', encoding='utf-8'))

print(f"Original database size: {len(db)} hands\n")

# Use (event_id, board) as composite key - keep only first occurrence
seen_keys = set()
cleaned_db = []
duplicates_removed = 0

for hand in db:
    event_id = hand.get('event_id')
    board = hand.get('board')
    key = (event_id, board)
    
    if key not in seen_keys:
        seen_keys.add(key)
        cleaned_db.append(hand)
    else:
        duplicates_removed += 1
        print(f"Removing duplicate: Event {event_id}, Board {board}")

print(f"\nCleaned database size: {len(cleaned_db)} hands")
print(f"Total duplicates removed: {duplicates_removed}\n")

# Verify the counts
events = {}
for hand in cleaned_db:
    event_id = int(hand.get('event_id', 0))
    if event_id not in events:
        events[event_id] = 0
    events[event_id] += 1

print(f"Number of events: {len(events)}")
print(f"\nHands per event (should all be 30):")

issues = []
for event_id in sorted(events.keys()):
    count = events[event_id]
    marker = "✓" if count == 30 else "✗"
    print(f"  Event {event_id}: {count} {marker}")
    if count != 30:
        issues.append((event_id, count))

# Save the cleaned database
with open('hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(cleaned_db, f, ensure_ascii=False, indent=2)

print(f"\n✅ Database consolidated: hands_database.json ({len(cleaned_db)} hands)")

if issues:
    print(f"\n⚠️ WARNING: {len(issues)} events don't have exactly 30 hands:")
    for event_id, count in issues:
        print(f"  Event {event_id}: {count} hands")
else:
    print(f"✅ All events have exactly 30 hands!")
