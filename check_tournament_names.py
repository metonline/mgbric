#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

with open('database.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

records_30_12 = [r for r in data if r.get('Tarih') == '30.12.2025']

print("Sample records for 30.12.2025:")
for i, rec in enumerate(records_30_12[:3]):
    print(f"\nRecord {i+1}:")
    print(f"  Tarih: '{rec.get('Tarih')}'")
    print(f"  Turnuva: '{rec.get('Turnuva')}'")
    print(f"  Oyuncu 1: '{rec.get('Oyuncu 1')}'")
    print(f"  Oyuncu 2: '{rec.get('Oyuncu 2')}'")
    print(f"  Sıra: {rec.get('Sıra')}")
    print(f"  Direction: {rec.get('Direction')}")

# Check if Turnuva field has any whitespace issues
tournaments = [r.get('Turnuva', '') for r in records_30_12]
print(f"\n\nTournament names (checking for whitespace):")
for t in set(tournaments):
    print(f"  Length: {len(t)}, Name: '{t}'")
    print(f"    Bytes: {t.encode('utf-8')}")
