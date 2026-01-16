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
print(f'Tournament: {data_29_12[0].get("Turnuva") if data_29_12 else "None"}')
champions_29_12 = [r for r in data_29_12 if r.get('Sira') == 1]
print(f'Champions (Sira=1): {len(champions_29_12)}')
ns_29_12 = [r for r in champions_29_12 if r.get('Direction') == 'NS']
ew_29_12 = [r for r in champions_29_12 if r.get('Direction') == 'EW']
print(f'  NS: {len(ns_29_12)}, EW: {len(ew_29_12)}')
if ns_29_12:
    print(f'  First NS: {ns_29_12[0]["Oyuncu 1"]} - {ns_29_12[0]["Oyuncu 2"]}')
if ew_29_12:
    print(f'  First EW: {ew_29_12[0]["Oyuncu 1"]} - {ew_29_12[0]["Oyuncu 2"]}')

print()
print('=== 30.12.2025 ===')
print(f'Total records: {len(data_30_12)}')
print(f'Tournament: {data_30_12[0].get("Turnuva") if data_30_12 else "None"}')
champions_30_12 = [r for r in data_30_12 if r.get('Sira') == 1]
print(f'Champions (Sira=1): {len(champions_30_12)}')
ns_30_12 = [r for r in champions_30_12 if r.get('Direction') == 'NS']
ew_30_12 = [r for r in champions_30_12 if r.get('Direction') == 'EW']
print(f'  NS: {len(ns_30_12)}, EW: {len(ew_30_12)}')
if ns_30_12:
    print(f'  First NS: {ns_30_12[0]["Oyuncu 1"]} - {ns_30_12[0]["Oyuncu 2"]}')
if ew_30_12:
    print(f'  First EW: {ew_30_12[0]["Oyuncu 1"]} - {ew_30_12[0]["Oyuncu 2"]}')
