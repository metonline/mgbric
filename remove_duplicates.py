#!/usr/bin/env python3
import json

db = json.load(open('database.json', encoding='utf-8'))

print(f"Before:")
print(f"  Legacy records: {len(db.get('legacy_records', []))}")
print(f"  Events: {len(db.get('events', {}))}")

# Remove events dict - it's all duplicate
db['events'] = {}

# Save
with open('database.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print(f"\nAfter:")
print(f"  Legacy records: {len(db.get('legacy_records', []))}")
print(f"  Events: {len(db.get('events', {}))}")
print(f"\n✅ Duplicates removed")
