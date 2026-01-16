#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

db = json.load(open('database.json', encoding='utf-8'))

# Check what dates exist for December 2025
dec_dates = set()
for r in db:
    tarih = r.get('Tarih', '')
    if tarih and '.12.2025' in tarih:
        dec_dates.add(tarih)

print('All December 2025 dates in database.json:')
for date in sorted(dec_dates):
    count = len([r for r in db if r.get('Tarih') == date])
    print(f'  {date}: {count} records')

# Check for 30.12
thirtytwelve = [r for r in db if r.get('Tarih', '').startswith('30.12')]
print(f'\nRecords starting with "30.12": {len(thirtytwelve)}')
if thirtytwelve:
    print(f'  First record Tarih: "{thirtytwelve[0].get("Tarih")}"')
