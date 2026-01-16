#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

with open('database.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 30.12.2025 kayıtlarını bul ve Turnuva adını düzelt
fixed_count = 0
for record in data:
    if record.get('Tarih') == '30.12.2025':
        old_turnuva = record.get('Turnuva', '')
        # Eğer eski tarih içeriyorsa (02-12 veya 03-12), düzelt
        if '02-12-2025' in old_turnuva or '03-12-2025' in old_turnuva:
            # 30.12.2025 için generic bir ad ver
            record['Turnuva'] = 'Çarşamba Turnuvası Sonuçları (30-12-2025)'
            fixed_count += 1

print(f'Düzeltilen kayıt: {fixed_count}')

# Kaydet
with open('database.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('✅ database.json güncellendi')

# Kontrol et
with open('database.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

records_30_12 = [r for r in data if r.get('Tarih') == '30.12.2025']
tournaments = {}
for r in records_30_12:
    turnuva = r.get('Turnuva', 'N/A')
    tournaments[turnuva] = tournaments.get(turnuva, 0) + 1

print(f'\n30.12.2025 Yeni Turnuva Dağılımı:')
for t, count in tournaments.items():
    print(f'  [{count}] {t}')
