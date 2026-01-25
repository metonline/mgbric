#!/usr/bin/env python3
"""
Fetch all hands from vugraph for 01.01.2026 to 24.01.2026
"""

import json
from event_registry import EventRegistry

# Load registry
er = EventRegistry()

# Get all event mappings
all_mappings = er._event_to_date  # {event_id: date}

print(f"📊 Total events in registry: {len(all_mappings)}")

# Find events in date range
events_in_range = {}
for event_id, date in all_mappings.items():
    # Check if date is between 01.01.2026 and 24.01.2026
    if date and '2026' in date and '01' in date:
        try:
            day = int(date.split('.')[0])
            month = int(date.split('.')[1])
            year = int(date.split('.')[2])
            if year == 2026 and month == 1 and 1 <= day <= 24:
                events_in_range[event_id] = date
        except:
            pass

print(f"\n✅ Events 01.01.2026 - 24.01.2026: {len(events_in_range)}")
print("\nEvent IDs and dates:")
for event_id in sorted(events_in_range.keys(), key=lambda x: events_in_range[x]):
    date = events_in_range[event_id]
    name = er._event_to_name.get(event_id, 'N/A')
    print(f"  {event_id}: {date} - {name[:60]}")

print(f"\n📝 Total: {len(events_in_range)} events to fetch")
