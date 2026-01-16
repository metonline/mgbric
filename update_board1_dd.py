#!/usr/bin/env python3
"""
Update Board 1 with correct DD values
"""

import json

with open('app/www/hands_database.json', encoding='utf-8') as f:
    db = json.load(f)

boards = db['events']['hosgoru_04_01_2026']['boards']
board = boards['1']

# Board 1 correct values from solver
# S: N=2, S=2, E=11, W=11
# D: N=9, S=9, E=4, W=4
# H: N=11, S=11, E=2, W=2
# C: N=9, S=9, E=4, W=4
# NT: N=10, S=10, E=3, W=3

board['dd_analysis'] = {
    'S': {'N': 2, 'E': 11, 'S': 2, 'W': 11},
    'D': {'N': 9, 'E': 4, 'S': 9, 'W': 4},
    'H': {'N': 11, 'E': 2, 'S': 11, 'W': 2},
    'C': {'N': 9, 'E': 4, 'S': 9, 'W': 4},
    'NT': {'N': 10, 'E': 3, 'S': 10, 'W': 3}
}

with open('app/www/hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print("✓ Board 1 updated with correct DD values!")
print("\nDD Analysis for Board 1:")
print("Spades:   N=2  E=11 S=2  W=11")
print("Diamonds: N=9  E=4  S=9  W=4")
print("Hearts:   N=11 E=2  S=11 W=2")
print("Clubs:    N=9  E=4  S=9  W=4")
print("NT:       N=10 E=3  S=10 W=3")
print("\nRefresh your browser to see the updated values!")
