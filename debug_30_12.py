#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

db = json.load(open('database.json', encoding='utf-8'))

# 30.12.2025 ve 29.12.2025 kayıtlarını kontrol et
dates_to_check = ['30.12.2025', '29.12.2025']

for check_date in dates_to_check:
    records = [r for r in db if r.get('Tarih') == check_date]
    print(f"Tarih '{check_date}': {len(records)} kayıt")
    
    if records:
        print(f"  İlk kayıt Tarih alanı: '{records[0].get('Tarih')}'")
        print(f"  Type: {type(records[0].get('Tarih'))}")
        print(f"  Örnek: {records[0]}")
    print()

# Tüm Tarih değerlerini kontrol et
all_tarih_values = set()
for r in db:
    tarih = r.get('Tarih')
    if tarih and '12.2025' in str(tarih):
        all_tarih_values.add(tarih)

print(f"\nTüm Aralık 2025 tarihleri:")
for date in sorted(all_tarih_values):
    count = len([r for r in db if r.get('Tarih') == date])
    print(f"  {date}: {count} kayıt")
