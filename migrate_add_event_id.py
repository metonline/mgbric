#!/usr/bin/env python3
"""
Migration script to add event_id to all hand records in hands_database.json
Maps dates to event IDs from database.json, and creates synthetic event IDs for missing dates
"""

import json
from pathlib import Path

# Load events and their dates
events_map = {}  # date -> event_id
try:
    with open('database.json', 'r', encoding='utf-8') as f:
        db_data = json.load(f)
    
    # Extract events and their dates
    events = db_data.get('events', {})
    for event_key, event_info in events.items():
        if event_key.startswith('event_'):
            event_id = event_key.replace('event_', '')
            date = event_info.get('date', '')
            if date:
                events_map[date] = event_id
                print(f"Found: {date} -> Event {event_id}")
except Exception as e:
    print(f"Error loading events: {e}")

print(f"\nLoaded {len(events_map)} events from database.json\n")

# Load hands database
with open('hands_database.json', 'r', encoding='utf-8') as f:
    hands_db = json.load(f)

if not isinstance(hands_db, list):
    print("ERROR: hands_database.json is not a list!")
    exit(1)

# Collect all unique dates
all_dates = set()
for hand in hands_db:
    date = hand.get('date', '')
    if date:
        all_dates.add(date)

all_dates = sorted(all_dates)
print(f"Found {len(all_dates)} unique dates in hands_database.json:")
for date in all_dates:
    if date in events_map:
        print(f"  {date} -> Event {events_map[date]} (in database.json)")
    else:
        print(f"  {date} -> MISSING (need synthetic ID)")

# Assign synthetic event IDs to missing dates
# Use a counter starting from a high number to avoid conflicts
next_synthetic_id = 400000

for date in all_dates:
    if date not in events_map:
        events_map[date] = str(next_synthetic_id)
        next_synthetic_id += 1

print(f"\n✓ Created {next_synthetic_id - 400000} synthetic event IDs\n")

# Add event_id to each hand record
updated = 0

for hand in hands_db:
    date = hand.get('date', '')
    
    if 'event_id' in hand and hand['event_id']:
        continue  # Already has valid event_id
    
    if date in events_map:
        hand['event_id'] = events_map[date]
        updated += 1

# Report
print(f"✓ Updated {updated} hand records with event_id")

# Save updated database
with open('hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(hands_db, f, indent=2, ensure_ascii=False)

print(f"✓ Saved updated hands_database.json with {len(hands_db)} total hands")

# Verify
print("\nVerification:")
print(f"  Total hands: {len(hands_db)}")
hands_with_event_id = [h for h in hands_db if h.get('event_id')]
print(f"  Hands with event_id: {len(hands_with_event_id)}")

if hands_with_event_id:
    sample = hands_with_event_id[0]
    print(f"\n  Sample hand:")
    print(f"    event_id: {sample['event_id']}")
    print(f"    date: {sample['date']}")
    print(f"    board: {sample['board']}")

# Show distribution of event_ids
event_id_counts = {}
for hand in hands_db:
    eid = hand.get('event_id')
    event_id_counts[eid] = event_id_counts.get(eid, 0) + 1

print(f"\n✓ Event ID distribution ({len(event_id_counts)} unique events):")
for eid in sorted(event_id_counts.keys()):
    count = event_id_counts[eid]
    print(f"  Event {eid}: {count} hands")

