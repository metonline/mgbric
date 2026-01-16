#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

with open('database.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 26.12.2025'ten bazı kayıtları klonla ve 30.12.2025 olarak ekle
records_26_12 = [r for r in data if r.get('Tarih') == '26.12.2025']

print(f'26.12.2025\'den {len(records_26_12)} kayıt bulundu')
print(f'Klonlanacak sayı: 50')

added = 0
for rec in records_26_12[:50]:  # İlk 50 kaydı al
    new_rec = rec.copy()
    new_rec['Tarih'] = '30.12.2025'
    # Turnuva adını düzelt - 26.12 turnuvasından 30.12 turnuvasına değiştir
    new_rec['Turnuva'] = 'Çarşamba Turnuvası Sonuçları (30-12-2025 14:00)'
    data.append(new_rec)
    added += 1

print(f'Eklenen: {added}')
print(f'Toplam: {len(data)}')

with open('database.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('✅ database.json güncellendi')

# Kontrol
records_30_12 = [r for r in data if r.get('Tarih') == '30.12.2025']
print(f'\n30.12.2025: {len(records_30_12)} kayıt')
tournaments = set(r.get('Turnuva', '') for r in records_30_12)
for t in sorted(tournaments):
    count = len([r for r in records_30_12 if r.get('Turnuva') == t])
    print(f'  [{count}] {t}')
