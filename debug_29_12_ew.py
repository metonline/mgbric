#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

with open('database.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Get 29.12.2025 data
data_29_12 = [r for r in data if r.get('Tarih') == '29.12.2025']

print('=== 29.12.2025 - ALL DATA ===')
print(f'Total records: {len(data_29_12)}')

# Count by direction
ns_records = [r for r in data_29_12 if r.get('Direction') == 'NS']
ew_records = [r for r in data_29_12 if r.get('Direction') == 'EW']
print(f'NS records: {len(ns_records)}')
print(f'EW records: {len(ew_records)}')

if ew_records:
    print(f'\nEW sample: {ew_records[0]}')
else:
    print('\nNo EW records found!')

# Show all records by direction and sira
print('\n=== NS Records by Sira ===')
ns_by_sira = {}
for r in ns_records:
    sira = r.get('Sıra')
    if sira not in ns_by_sira:
        ns_by_sira[sira] = []
    ns_by_sira[sira].append(r)

for sira in sorted(ns_by_sira.keys())[:5]:
    print(f'Sıra {sira}: {len(ns_by_sira[sira])} records')

print('\n=== EW Records by Sira ===')
ew_by_sira = {}
for r in ew_records:
    sira = r.get('Sıra')
    if sira not in ew_by_sira:
        ew_by_sira[sira] = []
    ew_by_sira[sira].append(r)

if ew_by_sira:
    for sira in sorted(ew_by_sira.keys())[:5]:
        print(f'Sıra {sira}: {len(ew_by_sira[sira])} records')
else:
    print('NO EW RECORDS AT ALL!')
