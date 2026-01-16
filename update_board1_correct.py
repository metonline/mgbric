#!/usr/bin/env python3
"""
Update Board 1 with CORRECT DD values from solver
"""

import json

with open('app/www/hands_database.json', encoding='utf-8') as f:
    db = json.load(f)

board = db['events']['hosgoru_04_01_2026']['boards']['1']

# Board 1 correct values (with complementary values calculated)
# NT: E=3, W=3 → N=10, S=10
# Spades: E=4, W=4 → N=9, S=9
# Hearts: E=2, W=2 → N=11, S=11
# Diamonds: E=4, W=4 → N=9, S=9
# Clubs: N=2, S=2 → E=11, W=11

dd_flat = {
    'NTN': 10, 'NTS': 10, 'NTE': 3, 'NTW': 3,
    'SN': 9, 'SS': 9, 'SE': 4, 'SW': 4,
    'HN': 11, 'HS': 11, 'HE': 2, 'HW': 2,
    'DN': 9, 'DS': 9, 'DE': 4, 'DW': 4,
    'CN': 2, 'CS': 2, 'CE': 11, 'CW': 11
}

board['dd_analysis'] = dd_flat

with open('app/www/hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print("✓ Board 1 updated with CORRECT DD values!")
print("\nDD Table:")
print("NT: N=10 S=10 E=3  W=3")
print("S:  N=9  S=9  E=4  W=4")
print("H:  N=11 S=11 E=2  W=2")
print("D:  N=9  S=9  E=4  W=4")
print("C:  N=2  S=2  E=11 W=11")
print("\nRefresh browser to see updated values!")
