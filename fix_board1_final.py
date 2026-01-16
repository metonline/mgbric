#!/usr/bin/env python3
import json

with open('app/www/hands_database.json', encoding='utf-8') as f:
    db = json.load(f)

board = db['events']['hosgoru_04_01_2026']['boards']['1']

# Set CORRECT values - all 20 flat keys
board['dd_analysis'] = {
    'SN': 2,   'SS': 2,   'SE': 11,  'SW': 11,
    'DN': 9,   'DS': 9,   'DE': 4,   'DW': 4,
    'HN': 11,  'HS': 11,  'HE': 2,   'HW': 2,
    'CN': 9,   'CS': 9,   'CE': 4,   'CW': 4,
    'NTN': 10, 'NTS': 10, 'NTE': 3,  'NTW': 3
}

with open('app/www/hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print("✓ Board 1 DD values corrected!")
