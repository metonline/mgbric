#!/usr/bin/env python3
import json

db = json.load(open('database.json', encoding='utf-8'))

print(f"Format: {type(db).__name__}")

if isinstance(db, list):
    print(f"Total records: {len(db)}")
    print(f"Sample record 1: {db[0]}")
    print(f"Sample record 2: {db[1]}")
    
    # Check unique dates
    dates = set(r.get('Tarih') for r in db if isinstance(r, dict))
    sorted_dates = sorted(dates)
    print(f"\nUnique dates ({len(dates)}):")
    print(f"First: {sorted_dates[0]}")
    print(f"Last: {sorted_dates[-1]}")
    print(f"Recent 5: {sorted_dates[-5:]}")
elif isinstance(db, dict):
    print(f"Dict format with keys: {list(db.keys())}")
    if 'events' in db:
        print(f"Events: {list(db['events'].keys())}")
