#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

# JSON dosyasını aç
with open('database.json', 'r', encoding='utf-8') as f:
    content = f.read()

print(f'JSON file size: {len(content)} bytes')

# Geçerli JSON mi?
try:
    data = json.loads(content)
    print(f'Valid JSON: Yes, {len(data)} records')
    
    # İlk 3 kaydı göster
    print('\nFirst 3 records:')
    for i, record in enumerate(data[:3]):
        print(f'{i}: Sıra={record.get("Sıra")}, Oyuncu1={record.get("Oyuncu 1")}, Oyuncu2={record.get("Oyuncu 2")}')
    
except json.JSONDecodeError as e:
    print(f'Invalid JSON: {e}')
    print(f'Error at position {e.pos}')
