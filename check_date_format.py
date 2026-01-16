#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

db = json.load(open('database.json', encoding='utf-8'))

# Get first 2 records for 30.12.2025
sample_records = [r for r in db if r.get('Tarih', '') == '30.12.2025'][:2]

print('Sample 30.12.2025 records from database.json:')
for i, record in enumerate(sample_records, 1):
    print(f'\nRecord {i}:')
    print(f'  Tarih: "{record.get("Tarih")}"')
    print(f'  Tarih type: {type(record.get("Tarih")).__name__}')
    print(f'  Sıra: {record.get("Sıra")}')

# Also check what dates exist
all_dates = set()
for r in db:
    tarih = r.get('Tarih', '')
    if tarih and '30' in tarih:
        all_dates.add(tarih)

print(f'\n\nAll dates containing "30":')
for date in sorted(all_dates)[:10]:
    print(f'  {date}')
