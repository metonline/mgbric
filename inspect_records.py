#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

with open('database.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Get 29.12.2025 and 30.12.2025 data
data_29_12 = [r for r in data if r.get('Tarih') == '29.12.2025']
data_30_12 = [r for r in data if r.get('Tarih') == '30.12.2025']

print('=== 29.12.2025 ===')
print(f'Total records: {len(data_29_12)}')
if data_29_12:
    print(f'Sample record: {json.dumps(data_29_12[0], ensure_ascii=False, indent=2)}')
    sira_values = set([r.get('Sıra') for r in data_29_12])
    print(f'Sıra values: {sorted(sira_values)[:10]}...')
    
print()
print('=== 30.12.2025 ===')
print(f'Total records: {len(data_30_12)}')
if data_30_12:
    print(f'Sample record: {json.dumps(data_30_12[0], ensure_ascii=False, indent=2)}')
    sira_values = set([r.get('Sıra') for r in data_30_12])
    print(f'Sıra values: {sorted(sira_values)[:10]}...')
