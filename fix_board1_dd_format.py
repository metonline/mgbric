#!/usr/bin/env python3
"""
Fix Board 1 DD format - convert to flat structure that HTML expects
HTML expects: {NTN: 9, NTS: 9, ..., SN: 2, SS: 2, ...}
"""

import json

with open('app/www/hands_database.json', encoding='utf-8') as f:
    db = json.load(f)

board = db['events']['hosgoru_04_01_2026']['boards']['1']

# Convert from nested to flat format
dd_flat = {
    # NT
    'NTN': 10, 'NTS': 10, 'NTE': 3, 'NTW': 3,
    # Spades
    'SN': 2, 'SS': 2, 'SE': 11, 'SW': 11,
    # Hearts
    'HN': 11, 'HS': 11, 'HE': 2, 'HW': 2,
    # Diamonds
    'DN': 9, 'DS': 9, 'DE': 4, 'DW': 4,
    # Clubs
    'CN': 9, 'CS': 9, 'CE': 4, 'CW': 4
}

board['dd_analysis'] = dd_flat

with open('app/www/hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print("✓ Board 1 DD format fixed!")
print("  Now in flat format: {NTN: 10, NTS: 10, SN: 2, ...}")
print("\nRefresh browser to see the values!")
