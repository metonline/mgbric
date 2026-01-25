#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check raw registry data for January 24th event"""

import json
from pathlib import Path

# Load the raw database.json which has the EventRegistry data
if Path('database.json').exists():
    registry_data = json.load(open('database.json', encoding='utf-8'))
    print(f"Registry loaded: {len(registry_data)} events\n")
    
    # Look for 24.01.2026
    events_24 = [e for e in registry_data if e.get('date') == '24.01.2026']
    print(f"Events for 24.01.2026: {len(events_24)}")
    
    if events_24:
        for e in events_24:
            print(f"  Event ID: {e.get('id')}")
            print(f"  Name: {e.get('name')}")
            print(f"  Date: {e.get('date')}")
    
    # Show last 5 events
    print(f"\nLast 5 events by date:")
    sorted_events = sorted(registry_data, key=lambda e: e.get('date', ''), reverse=True)
    for e in sorted_events[:5]:
        print(f"  {e.get('date')}: Event {e.get('id')} - {e.get('name')}")
else:
    print("database.json not found")
