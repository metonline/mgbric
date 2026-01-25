#!/usr/bin/env python3
"""Fix event 405659 date from 01.01.2026 to 24.01.2026"""
import json

# Load database
with open('hands_database.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

# Fix event 405659 date from '01.01.2026' to '24.01.2026'
updated_count = 0
for hand in db:
    if hand['event_id'] == 405659 and hand.get('date') == '01.01.2026':
        hand['date'] = '24.01.2026'
        updated_count += 1

# Save corrected database
with open('hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print(f"✓ Fixed {updated_count} hands for event 405659 - date changed from 01.01.2026 to 24.01.2026")

# Verify
with open('hands_database.json', 'r', encoding='utf-8') as f:
    db_verify = json.load(f)
    dates = sorted({h.get('date') for h in db_verify})
    print(f"Updated dates in database: {dates}")
