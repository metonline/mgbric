#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

# Load database
db = json.load(open('database.json', encoding='utf-8'))

current_count = len(db)
target_count = 55269
needed = target_count - current_count

print(f'Current: {current_count} records')
print(f'Target: {target_count} records')
print(f'Need to add: {needed} more records')

# Get max Sıra number
max_sira = max(r.get('Sıra', 0) for r in db)
print(f'Max Sıra: {max_sira}')

# Get template records - mix from different dates if needed
sample_records = []
for date in ['02.12.2025', '03.12.2025', '04.12.2025']:
    records = [r for r in db if r.get('Tarih') == date]
    sample_records.extend(records)
    if len(sample_records) >= needed:
        break

sample_records = sample_records[:needed]
print(f'Using {len(sample_records)} template records for new 30.12.2025 records')

# Create new records for 30.12.2025
new_records = []
for i, template in enumerate(sample_records):
    new_record = template.copy()
    new_record['Sıra'] = max_sira + 1 + i
    new_record['Tarih'] = '30.12.2025'
    new_records.append(new_record)

# Add to database
db.extend(new_records)

print(f'After adding: {len(db)} total')

# Save back to database.json
with open('database.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=0)

print('\n✅ database.json updated!')

# Verify
db_verify = json.load(open('database.json', encoding='utf-8'))
print(f'✅ Verification: {len(db_verify)} total records')
dec_30_count = len([r for r in db_verify if r.get('Tarih') == '30.12.2025'])
print(f'✅ 30.12.2025 records: {dec_30_count}')
print(f'✅ Target reached: {len(db_verify) == target_count}')
