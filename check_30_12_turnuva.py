#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

with open('database.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

records_30_12 = [r for r in data if r.get('Tarih') == '30.12.2025']

print(f'30.12.2025: {len(records_30_12)} kayıt')
print('\nTurnuva adları:')
tournaments = {}
for r in records_30_12:
    turnuva = r.get('Turnuva', 'N/A')
    tournaments[turnuva] = tournaments.get(turnuva, 0) + 1

for t, count in tournaments.items():
    print(f'  [{count}] {t}')
