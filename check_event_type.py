#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check event_id data type"""

import json

data = json.load(open('hands_database.json', encoding='utf-8'))

# Check event_id types
event_ids = set(h.get('event_id') for h in data)
print(f"Sample event_ids: {list(event_ids)[:5]}\n")

# Check both int and string
h405596_int = [h for h in data if h.get('event_id') == 405596]
h405596_str = [h for h in data if h.get('event_id') == '405596']

print(f"Matching event_id == 405596 (int): {len(h405596_int)}")
print(f"Matching event_id == '405596' (str): {len(h405596_str)}")

# Count per event regardless of type
events_count = {}
for h in data:
    eid = h.get('event_id')
    if eid not in events_count:
        events_count[eid] = 0
    events_count[eid] += 1

print(f"\nAll event counts:")
for eid in sorted(events_count.keys()):
    count = events_count[eid]
    marker = "✓" if count == 30 else "✗"
    print(f"  {eid} (type={type(eid).__name__}): {count} {marker}")

print(f"\nTotal hands: {len(data)}")
