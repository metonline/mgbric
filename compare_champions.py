#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

with open('database.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Get 29.12.2025 and 30.12.2025 data
data_29_12 = [r for r in data if r.get('Tarih') == '29.12.2025']
data_30_12 = [r for r in data if r.get('Tarih') == '30.12.2025']

print('=== 29.12.2025 - Champions (Sıra=1) ===')
champs_29 = [r for r in data_29_12 if r.get('Sıra') == 1]
print(f'Total Sıra=1: {len(champs_29)}')
ns_champs_29 = [r for r in champs_29 if r.get('Direction') == 'NS']
ew_champs_29 = [r for r in champs_29 if r.get('Direction') == 'EW']
print(f'NS Champions: {len(ns_champs_29)}')
print(f'EW Champions: {len(ew_champs_29)}')

# Get unique pairs for NS
ns_pairs_29 = set()
for r in ns_champs_29:
    pair = (r['Oyuncu 1'], r['Oyuncu 2'])
    ns_pairs_29.add(pair)
print(f'Unique NS pairs: {len(ns_pairs_29)}')
for pair in list(ns_pairs_29)[:3]:
    print(f'  - {pair[0]} - {pair[1]}')

# Get unique pairs for EW
ew_pairs_29 = set()
for r in ew_champs_29:
    pair = (r['Oyuncu 1'], r['Oyuncu 2'])
    ew_pairs_29.add(pair)
print(f'Unique EW pairs: {len(ew_pairs_29)}')
for pair in list(ew_pairs_29)[:3]:
    print(f'  - {pair[0]} - {pair[1]}')

print()
print('=== 30.12.2025 - Champions (Sıra=1) ===')
champs_30 = [r for r in data_30_12 if r.get('Sıra') == 1]
print(f'Total Sıra=1: {len(champs_30)}')
ns_champs_30 = [r for r in champs_30 if r.get('Direction') == 'NS']
ew_champs_30 = [r for r in champs_30 if r.get('Direction') == 'EW']
print(f'NS Champions: {len(ns_champs_30)}')
print(f'EW Champions: {len(ew_champs_30)}')

# Get unique pairs for NS
ns_pairs_30 = set()
for r in ns_champs_30:
    pair = (r['Oyuncu 1'], r['Oyuncu 2'])
    ns_pairs_30.add(pair)
print(f'Unique NS pairs: {len(ns_pairs_30)}')
for pair in list(ns_pairs_30)[:3]:
    print(f'  - {pair[0]} - {pair[1]}')

# Get unique pairs for EW
ew_pairs_30 = set()
for r in ew_champs_30:
    pair = (r['Oyuncu 1'], r['Oyuncu 2'])
    ew_pairs_30.add(pair)
print(f'Unique EW pairs: {len(ew_pairs_30)}')
for pair in list(ew_pairs_30)[:3]:
    print(f'  - {pair[0]} - {pair[1]}')
