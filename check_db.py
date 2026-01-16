#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from datetime import datetime

db_file = r'C:\Users\metin\Desktop\BRIC\database.json'

with open(db_file, 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

print(f"📊 Toplam kayıt: {len(data)}")
print(f"\n📅 Son 5 kaydın tarihleri:\n")

for i, record in enumerate(data[-5:], 1):
    tarih = record.get('Tarih', 'N/A')
    oyuncu = record.get('Oyuncu 1', 'N/A')[:20]
    print(f"{i}. {tarih} - {oyuncu}")

# Benzersiz tarihleri al ve sırala
unique_dates = sorted(set([r.get('Tarih') for r in data if r.get('Tarih')]), 
                     key=lambda x: tuple(map(int, x.split('.')[::-1])))

print(f"\n📆 Tüm tarihlerin aralığı:")
print(f"   En eski: {unique_dates[0] if unique_dates else 'N/A'}")
print(f"   En yeni: {unique_dates[-1] if unique_dates else 'N/A'}")
print(f"\n✅ database.json güncellendi mi? {datetime.fromtimestamp(json.load(open(db_file))[-1].get('Sıra', 0) if data else 0)}")
