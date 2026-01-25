#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final verification of database integrity"""

import json

db = json.load(open('hands_database.json', encoding='utf-8'))

# Count hands per event
events = {}
for h in db:
    eid = int(h.get('event_id', 0)) if h.get('event_id') else 0
    if eid not in events:
        events[eid] = 0
    events[eid] += 1

print(f"Total hands: {len(db)}")
print(f"Total events: {len(events)}\n")

# Expected: 23 events × 30 hands = 690 hands
print(f"Events with hand counts:")
total_ok = 0
for eid in sorted(events.keys()):
    count = events[eid]
    marker = '✓' if count == 30 else '✗'
    print(f"  Event {eid}: {count} hands {marker}")
    if count == 30:
        total_ok += 1

print(f"\nExpected: 23 events × 30 hands = 690 total hands")
print(f"Actual: {len(events)} events × {len(db) // len(events) if events else 0} avg hands = {len(db)} total hands")

if len(events) == 23 and len(db) == 690:
    print(f"\n✅ Database is properly consolidated!")
else:
    print(f"\n⚠️ Database needs attention")
    print(f"   Total hands: {len(db)} (expected 690)")
    print(f"   Total events: {len(events)} (expected 23)")
