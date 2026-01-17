#!/usr/bin/env python3
import json

db = json.load(open('database.json', encoding='utf-8'))

legacy = db.get('legacy_records', [])
events = db.get('events', {})

print(f"Legacy records: {len(legacy)}")
print(f"Events count: {len(events)}")

# Count records in events
total_event_records = 0
for event_data in events.values():
    ns = event_data.get('results', {}).get('NS', [])
    ew = event_data.get('results', {}).get('EW', [])
    total_event_records += len(ns) + len(ew)

print(f"Total records in events: {total_event_records}")
print(f"GRAND TOTAL: {len(legacy) + total_event_records}")

if legacy:
    print(f"\nSample legacy record:")
    print(f"  Tarih: {legacy[0].get('Tarih')}")
    print(f"  Oyuncu: {legacy[0].get('Oyuncu 1')}")
