#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

# Load database
with open('database.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total records in database.json: {len(data)}")
print(f"Expected from run_bot.py console: 54969")
print(f"Difference: {54969 - len(data)}")
print()

# Check Sıra field
sira_0 = len([r for r in data if str(r.get('Sıra', '0')) == '0'])
sira_gt0 = len([r for r in data if str(r.get('Sıra', '0')).isdigit() and int(r.get('Sıra', '0')) > 0])
sira_empty = len([r for r in data if not r.get('Sıra')])

print(f"Sıra = 0: {sira_0}")
print(f"Sıra > 0: {sira_gt0}")
print(f"Sıra empty: {sira_empty}")
print(f"Total accounted: {sira_0 + sira_gt0 + sira_empty}")
print()

# Check for null/empty fields
oyuncu1_empty = len([r for r in data if not r.get('Oyuncu 1')])
oyuncu2_empty = len([r for r in data if not r.get('Oyuncu 2')])
skor_empty = len([r for r in data if not r.get('Skor')])

print(f"Oyuncu 1 empty: {oyuncu1_empty}")
print(f"Oyuncu 2 empty: {oyuncu2_empty}")
print(f"Skor empty: {skor_empty}")
