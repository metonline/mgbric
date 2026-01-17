#!/usr/bin/env python3
import json
from datetime import datetime

db = json.load(open('database.json', encoding='utf-8'))
print(f"Total records: {len(db)}")
print(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
print("\nLatest 5 entries:")
for r in db[-5:]:
    hands_status = "✓ Has Hands" if "Hands" in r else "✗ No Hands"
    print(f"  {r['Tarih']} | {r['Turnuva'][:35]:35} | {hands_status}")

# Count how many records have hands
hands_count = sum(1 for r in db if "Hands" in r)
print(f"\nRecords with hands: {hands_count}/{len(db)}")
