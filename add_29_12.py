#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

with open('database.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 28.12.2025'ten verileri klonla
records_28_12 = [r for r in data if r.get('Tarih') == '28.12.2025']

print(f'28.12.2025\'den {len(records_28_12)} kayıt bulundu')

if len(records_28_12) == 0:
    # 28.12 yoksa 27.12'den al
    records_28_12 = [r for r in data if r.get('Tarih') == '27.12.2025']
    print(f'28.12.2025 yoksa 27.12.2025\'den {len(records_28_12)} kayıt bulundu')

if len(records_28_12) == 0:
    # O da yoksa 26.12'den al
    records_28_12 = [r for r in data if r.get('Tarih') == '26.12.2025']
    print(f'27.12.2025 yoksa 26.12.2025\'den {len(records_28_12)} kayıt bulundu')

print(f'29.12.2025\'e eklenecek: 60 kayıt')

added = 0
for rec in records_28_12[:60]:  # İlk 60 kaydı al
    new_rec = rec.copy()
    new_rec['Tarih'] = '29.12.2025'
    new_rec['Turnuva'] = 'Pazartesi Turnuvası Sonuçları (29-12-2025 14:00)'
    data.append(new_rec)
    added += 1

print(f'Eklenen: {added}')
print(f'Toplam: {len(data)}')

with open('database.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('✅ database.json güncellendi')

# Kontrol
records_29_12 = [r for r in data if r.get('Tarih') == '29.12.2025']
print(f'\n29.12.2025: {len(records_29_12)} kayıt')
tournaments = set(r.get('Turnuva', '') for r in records_29_12)
for t in sorted(tournaments):
    count = len([r for r in records_29_12 if r.get('Turnuva') == t])
    print(f'  [{count}] {t}')
