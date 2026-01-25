#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Remove duplicate hands from the database, keeping only one copy per (event_id, board)"""

import json

db = json.load(open('hands_database.json'))

print(f"Original database size: {len(db)} hands\n")

# Remove duplicates: keep first occurrence of each (event_id, board)
seen = {}
cleaned_db = []

for hand in db:
    event_id = hand.get('event_id')
    board = hand.get('board')
    key = (event_id, board)
    
    if key not in seen:
        seen[key] = True
        cleaned_db.append(hand)

print(f"Cleaned database size: {len(cleaned_db)} hands")
print(f"Removed {len(db) - len(cleaned_db)} duplicate hands\n")

# Verify the counts
events = set(int(h.get('event_id', 0)) for h in cleaned_db)
print(f"Number of events: {len(events)}")
print(f"Hands per event (should all be 30):")

for event_id in sorted(events):
    count = len([h for h in cleaned_db if int(h.get('event_id', 0)) == event_id])
    marker = "✓" if count == 30 else "✗"
    print(f"  Event {event_id}: {count} {marker}")

# Save the cleaned database
with open('hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(cleaned_db, f, ensure_ascii=False, indent=2)

print(f"\n✅ Database saved: hands_database.json ({len(cleaned_db)} hands)")
