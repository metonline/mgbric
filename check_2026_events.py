#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check what 2026 events are available in the registry"""

from unified_fetch import EventRegistry

registry = EventRegistry()
all_events = registry.get_all_events()  # Returns {date: event_id}

# Filter to 2026 events
events_2026 = {}
for date_str, event_id in all_events.items():
    if not date_str or date_str == 'unknown':
        continue
    try:
        parts = date_str.split('.')
        if len(parts) == 3:
            year = int(parts[2])
            if year == 2026:
                events_2026[date_str] = event_id
    except:
        pass

print(f"Total 2026 events: {len(events_2026)}")
print(f"\nAll 2026 events sorted by date:")
print("=" * 60)

for date_str in sorted(events_2026.keys()):
    event_id = events_2026[date_str]
    print(f"  {date_str}: Event {event_id}")

print("=" * 60)

# Check specifically for 23rd and 24th
print(f"\nJanuary 23rd events:")
events_23 = {d: e for d, e in events_2026.items() if d.startswith('23.')}
if events_23:
    for d, e in events_23.items():
        print(f"  {d}: Event {e}")
else:
    print("  None found")

print(f"\nJanuary 24th events:")
events_24 = {d: e for d, e in events_2026.items() if d.startswith('24.')}
if events_24:
    for d, e in events_24.items():
        print(f"  {d}: Event {e}")
else:
    print("  None found")
