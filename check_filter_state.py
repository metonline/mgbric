#!/usr/bin/env python3
"""Check database state and filter logic"""
import json
from datetime import datetime
from collections import Counter

# Load database
with open('database.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

legacy_records = db.get('legacy_records', [])
events = db.get('events', {})

print(f"📊 Database Durumu:")
print(f"   Legacy records: {len(legacy_records)}")
print(f"   Events: {len(events)}")
print(f"   Total: {len(legacy_records) + len(events)}")

# Get all dates
all_dates = []
for record in legacy_records:
    if record.get('Tarih'):
        all_dates.append(record['Tarih'])

all_dates_sorted = sorted(set(all_dates))
print(f"\n📅 Tarih Aralığı:")
if all_dates_sorted:
    print(f"   İlk: {all_dates_sorted[0]}")
    print(f"   Son: {all_dates_sorted[-1]}")
    print(f"   Benzersiz tarih: {len(all_dates_sorted)}")

# Get dates for 2026
dates_2026 = [d for d in all_dates_sorted if d.endswith('.2026')]
print(f"\n🎯 2026 Tarihleri: {len(dates_2026)} tarihi")
if dates_2026:
    print(f"   First: {dates_2026[0]}")
    print(f"   Last: {dates_2026[-1]}")

# Get dates for January 2026
dates_01_2026 = [d for d in all_dates_sorted if '.01.2026' in d]
print(f"\n📌 Ocak 2026 Tarihleri: {len(dates_01_2026)} kayıt")
if dates_01_2026:
    print(f"   Dates: {sorted(dates_01_2026)}")

# Find max date (latest)
max_date = max(all_dates_sorted) if all_dates_sorted else None
print(f"\n⭐ Son güncellenen tarih (MAX): {max_date}")

# Count records per date for January 2026
date_counter = Counter(all_dates)
jan_2026_counts = {d: date_counter[d] for d in dates_01_2026}
print(f"\n📋 Ocak 2026 Tarihlerine göre kayıt sayısı:")
for date in sorted(jan_2026_counts.keys()):
    print(f"   {date}: {jan_2026_counts[date]} kayıt")
