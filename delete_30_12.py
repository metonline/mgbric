#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

with open('database.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 30.12.2025 kayıtlarını filtrele ve çıkar
original_count = len(data)
data = [r for r in data if r.get('Tarih') != '30.12.2025']
removed_count = original_count - len(data)

print(f'30.12.2025 silinen kayıt: {removed_count}')
print(f'Kalan toplam: {len(data)}')

# Kaydet
with open('database.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('✅ database.json güncellendi - 30.12.2025 verisi silindi')
