#!/usr/bin/env python3
import requests
import json
from datetime import datetime

# Test flow
print("=== TARIH FILTRESI TEST FLOW ===\n")

# 1. Database yükle
print("1️⃣  Veritabanı yükleniyor...")
r = requests.get('http://localhost:5000/get_database', timeout=5)
data = r.json()
print(f"   ✓ {len(data)} kayıt yüklendi\n")

# 2. "Bu Ay" filtresini simüle et
print("2️⃣  'Bu Ay' filtresi simüle ediliyor...")
today = datetime.now()
start_date = datetime(today.year, today.month, 1)
if today.month == 12:
    end_date = datetime(today.year, 12, 31)
else:
    end_date = datetime(today.year, today.month + 1, 1)
    from datetime import timedelta
    end_date -= timedelta(days=1)

def parse_date(date_str):
    day, month, year = date_str.split('.')
    return datetime(int(year), int(month), int(day))

filtered = []
for record in data:
    try:
        record_date = parse_date(record['Tarih'])
        if start_date <= record_date <= end_date and int(record['Sıra']) > 0:
            filtered.append(record)
    except:
        pass

print(f"   ✓ {len(filtered)} kayıt filtrelendi\n")

# 3. Tab 1: Şampiyonlar
print("3️⃣  Tab 1 - Şampiyonlar (Sıra=1):")
champions = [r for r in filtered if str(r['Sıra']) == '1']
print(f"   ✓ {len(champions)} şampiyon bulundu")

# Deduplication
seen = {}
unique = []
for champ in champions:
    key = f"{champ['Oyuncu 1']}|{champ['Oyuncu 2']}|{champ['Direction']}"
    if key not in seen:
        seen[key] = True
        unique.append(champ)

ns = [c for c in unique if c['Direction'] == 'NS']
ew = [c for c in unique if c['Direction'] == 'EW']
print(f"   - NS: {len(ns)} | EW: {len(ew)}\n")

# 4. Tab 2: Kuzey-Güney
print("4️⃣  Tab 2 - Kuzey-Güney (Direction=NS):")
ns_all = [r for r in filtered if r['Direction'] == 'NS']
ns_sorted = sorted(ns_all, key=lambda x: int(x['Sıra']) if isinstance(x['Sıra'], (int, str)) and str(x['Sıra']).isdigit() else 999)
print(f"   ✓ {len(ns_sorted)} sonuç")
if ns_sorted:
    print(f"   - Örnek: [{ns_sorted[0]['Sıra']}] {ns_sorted[0]['Oyuncu 1']} vs {ns_sorted[0]['Oyuncu 2']} - {ns_sorted[0]['Skor']}%\n")

# 5. Tab 3: Doğu-Batı
print("5️⃣  Tab 3 - Doğu-Batı (Direction=EW):")
ew_all = [r for r in filtered if r['Direction'] == 'EW']
ew_sorted = sorted(ew_all, key=lambda x: int(x['Sıra']) if isinstance(x['Sıra'], (int, str)) and str(x['Sıra']).isdigit() else 999)
print(f"   ✓ {len(ew_sorted)} sonuç")
if ew_sorted:
    print(f"   - Örnek: [{ew_sorted[0]['Sıra']}] {ew_sorted[0]['Oyuncu 1']} vs {ew_sorted[0]['Oyuncu 2']} - {ew_sorted[0]['Skor']}%\n")

print("✅ FLOW BİTTİ - Modal açılıp 3 sayfa gösterilmeli")
