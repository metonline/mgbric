#!/usr/bin/env python3
"""Get the ACTUAL maximum date"""
import json

with open('database.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

legacy = db.get('legacy_records', [])
dates = []
for record in legacy:
    tarih = record.get('Tarih')
    if tarih:
        try:
            day, month, year = tarih.split('.')
            # Sort by year then month then day
            dates.append((int(year), int(month), int(day), tarih))
        except:
            pass

dates.sort(reverse=True)
if dates:
    print("İlk 5 en son tarih:")
    for i, (y, m, d, tarih) in enumerate(dates[:5]):
        print(f"{i+1}. {tarih}")
