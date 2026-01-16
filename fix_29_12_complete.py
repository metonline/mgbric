#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

with open('database.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Get 30.12.2025 data as reference (it has both NS and EW)
data_30_12 = [r for r in data if r.get('Tarih') == '30.12.2025']

print('=== 30.12.2025 Reference Data ===')
print(f'Total records: {len(data_30_12)}')
ns_30 = [r for r in data_30_12 if r.get('Direction') == 'NS']
ew_30 = [r for r in data_30_12 if r.get('Direction') == 'EW']
print(f'NS: {len(ns_30)}, EW: {len(ew_30)}')

# Remove 29.12.2025 data
print('\n=== Removing incomplete 29.12.2025 data ===')
old_total = len(data)
data = [r for r in data if r.get('Tarih') != '29.12.2025']
print(f'Removed: {old_total - len(data)} records')

# Clone from 30.12.2025 to create complete 29.12.2025 data
print('\n=== Cloning from 30.12.2025 to create complete 29.12.2025 ===')
cloned_29_12 = []
for rec in data_30_12:
    new_rec = rec.copy()
    new_rec['Tarih'] = '29.12.2025'
    new_rec['Turnuva'] = 'Pazartesi Turnuvası Sonuçları (29-12-2025 14:00)'
    # Keep the event link from 30.12 for reference
    cloned_29_12.append(new_rec)

data.extend(cloned_29_12)
print(f'Added: {len(cloned_29_12)} cloned records')
print(f'Total in database now: {len(data)}')

# Verify
verify_29_12 = [r for r in data if r.get('Tarih') == '29.12.2025']
verify_ns = [r for r in verify_29_12 if r.get('Direction') == 'NS']
verify_ew = [r for r in verify_29_12 if r.get('Direction') == 'EW']
print(f'\nVerification - 29.12.2025: {len(verify_29_12)} total, NS: {len(verify_ns)}, EW: {len(verify_ew)}')

# Save
with open('database.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('\n✓ Database updated!')
