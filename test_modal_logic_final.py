#!/usr/bin/env python3
"""Test modal açılışı ve veri render'ı"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

print("🧪 Testing Modal Opening with Fixed loadDatabase()")
print("=" * 60)

# Load page
print("\n1️⃣  Simulating page load and filter click...")
time.sleep(2)  # Server boot time

# Get database
print("\n2️⃣  Getting database...")
response = requests.get(f"{BASE_URL}/get_database")
if response.status_code != 200:
    print(f"✗ Failed: {response.status_code}")
    exit(1)

data = response.json()
print(f"✓ Database: {len(data)} records")

# Simulate loadDatabase() with period='currentMonth'
print("\n3️⃣  Simulating loadDatabase('currentMonth')...")

from datetime import datetime

period = 'currentMonth'
today = datetime.now()
first_day = datetime(today.year, today.month, 1)
last_day = today

def parse_date(date_str):
    try:
        day, month, year = date_str.split('.')
        return datetime(int(year), int(month), int(day))
    except:
        return None

filtered = []
for record in data:
    if 'Tarih' in record and record['Tarih']:
        rec_date = parse_date(record['Tarih'])
        if rec_date and first_day <= rec_date <= last_day:
            filtered.append(record)

print(f"✓ Filtered for '{period}': {len(filtered)} records")

# Test showGlobalRangeTab logic
print("\n4️⃣  Testing Tab 1 (Şampiyonlar)...")

champions = [r for r in filtered if str(r.get('Sıra', '0')).strip() in ['1', 1]]
print(f"   Found {len(champions)} champion records (Sıra=1)")

# Deduplicate
seen = {}
unique = []
for champ in champions:
    key = f"{champ.get('Oyuncu 1', '')}|{champ.get('Oyuncu 2', '')}|{champ.get('Direction', '')}"
    if key not in seen:
        seen[key] = True
        unique.append(champ)

print(f"   After dedup: {len(unique)} unique champions")

ns_champs = [c for c in unique if c.get('Direction') == 'NS']
ew_champs = [c for c in unique if c.get('Direction') == 'EW']

print(f"   NS champions: {len(ns_champs)}")
print(f"   EW champions: {len(ew_champs)}")

# Sample champions
if ns_champs:
    champ = ns_champs[0]
    print(f"   Sample: {champ.get('Oyuncu 1')} vs {champ.get('Oyuncu 2')} ({champ.get('Skor')}%)")

print("\n5️⃣  Testing Tab 2 (Sonuçlar)...")

results = [r for r in filtered if int(r.get('Sıra', 0)) > 0]
results_sorted = sorted(results, key=lambda x: int(x.get('Sıra', 999)))
print(f"   Found {len(results_sorted)} results (Sıra > 0)")

if results_sorted:
    result = results_sorted[0]
    print(f"   Sample: [{result.get('Sıra')}] {result.get('Oyuncu 1')} - {result.get('Oyuncu 2')} ({result.get('Direction')} {result.get('Skor')}%)")

print("\n" + "=" * 60)
print("✅ Modal logic test completed!")
print("\n📌 Next: Open browser and click filter buttons:")
print("   1. Sayfayı F5 ile yenile")
print("   2. 'Bu Ay' butonuna tıkla")
print("   3. Modal açılıp Şampiyonlar gösterilmeli")
print("   4. 'Sonraki' → tıkla, Sonuçlar gösterilmeli")
print("   5. 'Önceki' ← tıkla, Şampiyonlar geri dönmeli")
