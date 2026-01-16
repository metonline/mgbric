#!/usr/bin/env python3
"""Test globalRangeModal functionality"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

print("🔧 Testing Global Range Modal...")
print()

# Test 1: Load database
print("1️⃣  Loading database...")
response = requests.get(f"{BASE_URL}/get_database")
if response.status_code == 200:
    data = response.json()
    print(f"✓ Database loaded: {len(data)} records")
else:
    print(f"✗ Failed to load database: {response.status_code}")
    exit(1)

# Test 2: Filter "Bu Ay" (December 2025)
print()
print("2️⃣  Testing 'Bu Ay' filter...")

# Current date is Dec 2025
from datetime import datetime

def parse_date(date_str):
    """Parse DD.MM.YYYY format"""
    day, month, year = date_str.split('.')
    return datetime(int(year), int(month), int(day))

today = datetime.now()
first_day = datetime(today.year, today.month, 1)
last_day = datetime(today.year, today.month, 28)  # Approximate

filtered = []
for record in data:
    if 'Tarih' in record and record['Tarih']:
        try:
            record_date = parse_date(record['Tarih'])
            if first_day <= record_date <= today:
                filtered.append(record)
        except:
            pass

print(f"✓ 'Bu Ay' filter: {len(filtered)} records")

# Test 3: Check if globalRangeModal functions would work
print()
print("3️⃣  Verifying data structure...")

# Get champions (Sıra == 1)
champions = [r for r in filtered if str(r.get('Sıra', '')).strip() == '1']
print(f"✓ Champions found: {len(champions)}")

# Get results (Sıra > 0)
results = [r for r in filtered if int(r.get('Sıra', 0)) > 0]
results_sorted = sorted(results, key=lambda x: int(x.get('Sıra', 999)))
print(f"✓ Results found: {len(results_sorted)}")

# Test 4: Check modal HTML elements
print()
print("4️⃣  Checking HTML elements in index.html...")

with open('index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()
    
checks = [
    ('globalRangeModal', 'id="globalRangeModal"'),
    ('rangeModalContent', 'id="rangeModalContent"'),
    ('rangePageIndicator', 'id="rangePageIndicator"'),
    ('rangePrevBtn', 'id="rangePrevBtn"'),
    ('rangeNextBtn', 'id="rangeNextBtn"'),
    ('rangeModalTitle', 'id="rangeModalTitle"'),
    ('closeGlobalRangeModal', 'closeGlobalRangeModal()'),
    ('showGlobalRangeTab', 'showGlobalRangeTab('),
]

for name, pattern in checks:
    if pattern in html_content:
        print(f"  ✓ {name}")
    else:
        print(f"  ✗ {name} MISSING")

# Test 5: Check JavaScript functions
print()
print("5️⃣  Checking JavaScript functions in script.js...")

with open('script.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

js_checks = [
    ('openGlobalRangeModal', 'function openGlobalRangeModal'),
    ('closeGlobalRangeModal', 'function closeGlobalRangeModal'),
    ('showGlobalRangeTab', 'function showGlobalRangeTab'),
]

for name, pattern in js_checks:
    if pattern in js_content:
        print(f"  ✓ {name}")
    else:
        print(f"  ✗ {name} MISSING")

print()
print("✅ All tests completed!")
print()
print("🚀 Next steps:")
print("  1. Open http://localhost:5000 in browser")
print("  2. Click 'Bu Ay', 'Bu Yıl', 'Son 3 Yıl', or '2020'den Beri' buttons")
print("  3. Verify 2-page modal opens with Champions and Results tabs")
print("  4. Test navigation between pages")
