#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '/c/Users/metin/Desktop/BRIC')

from database_manager import VugraphScraper
import json

print('🔄 Vugraph\'tan verileri çekiliyor... (biraz zaman alabilir)')
scraper = VugraphScraper()

# Tüm turnuvaları scrap et
all_records = scraper.scrape_all()
print(f'✅ Çekilen toplam: {len(all_records)} kayıt')

# Database'yi yükle
with open('database.json', 'r', encoding='utf-8') as f:
    db_data = json.load(f)

# Yeni kayıtları ekle (duplikat kontrol zaten yapılıyor)
initial_count = len(db_data)
for rec in all_records:
    # Aynı kaydı kontrol et
    exists = any(
        r.get('Tarih') == rec.get('Tarih') and
        r.get('Oyuncu 1') == rec.get('Oyuncu 1') and
        r.get('Oyuncu 2') == rec.get('Oyuncu 2') and
        r.get('Skor') == rec.get('Skor')
        for r in db_data
    )
    if not exists:
        db_data.append(rec)

added = len(db_data) - initial_count
print(f'Eklenen yeni kayıt: {added}')
print(f'Toplam kayıt: {len(db_data)}')

# Kaydet
with open('database.json', 'w', encoding='utf-8') as f:
    json.dump(db_data, f, ensure_ascii=False, indent=2)

print('✅ database.json güncellendi')

# Kontrol
records_30_12 = [r for r in db_data if r.get('Tarih') == '30.12.2025']
print(f'\n30.12.2025: {len(records_30_12)} kayıt')
