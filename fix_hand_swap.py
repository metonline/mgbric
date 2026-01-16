#!/usr/bin/env python3
"""
Fix the hand assignment issue:
- East hand showing at South -> move to East  
- North showing at West -> move to North
- By symmetry: South showing at East -> move to South
- By symmetry: West showing at North -> move to West
"""

import json

# Load current corrupted database
with open('app/www/hands_database.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

boards = db['events']['hosgoru_04_01_2026']['boards']

print("="*70)
print("FIXING HAND ASSIGNMENT ISSUE - ALL 30 BOARDS")
print("="*70)

# Fix all 30 boards by swapping: N↔W and S↔E
for board_num in range(1, 31):
    board_key = str(board_num)
    if board_key not in boards:
        continue
    
    board = boards[board_key]
    original_hands = dict(board['hands'])
    
    # Apply the reverse transformation:
    # Currently: N has W's cards, S has E's cards, E has S's cards, W has N's cards
    # We want: N has N's cards, S has S's cards, E has E's cards, W has W's cards
    board['hands']['North'] = original_hands['West']
    board['hands']['South'] = original_hands['East']
    board['hands']['East'] = original_hands['South']
    board['hands']['West'] = original_hands['North']
    
    print(f"✅ Board {board_num}: Hands corrected (N↔W, S↔E)")

# Save
with open('app/www/hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print("\n" + "="*70)
print(f"✅ Fixed all 30 boards")
print(f"✅ Database saved: app/www/hands_database.json")
print("="*70)

# Verify
with open('app/www/hands_database.json', 'r', encoding='utf-8') as f:
    db_check = json.load(f)

print("\n✅ Verification - Board 1 hands:")
b1 = db_check['events']['hosgoru_04_01_2026']['boards']['1']
for player in ['North', 'South', 'East', 'West']:
    hand = b1['hands'][player]
    suits_str = ' '.join([f'{s}{hand[s]}' for s in ['S', 'H', 'D', 'C']])
    print(f"  {player:6}: {suits_str}")
