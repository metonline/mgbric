#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

with open('database.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

records_30_12 = [r for r in data if r.get('Tarih') == '30.12.2025']
print(f'Total 30.12.2025 records: {len(records_30_12)}')

tournaments = set(r.get('Turnuva', '') for r in records_30_12)
print(f'Unique tournaments: {len(tournaments)}')

for t in sorted(tournaments):
    print(f'  - {t}')
