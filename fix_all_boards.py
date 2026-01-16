#!/usr/bin/env python3
"""
Fix hand directions for boards 2-30 (same rotation pattern as Board 1)
Pattern: N→W, S→E, E→N, W→S
"""

import json

# Load database
with open('app/www/hands_database.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

boards = db['events']['hosgoru_04_01_2026']['boards']

print("\n" + "="*70)
print("FIXING HAND DIRECTIONS FOR BOARDS 2-30".center(70))
print("="*70)

corrected = 0

for board_num in range(2, 31):
    board_key = str(board_num)
    if board_key not in boards:
        continue
    
    board = boards[board_key]
    hands = board['hands']
    
    # Apply rotation: N→W, S→E, E→N, W→S
    original_hands = {
        'North': hands['North'].copy(),
        'South': hands['South'].copy(),
        'East': hands['East'].copy(),
        'West': hands['West'].copy(),
    }
    
    # Rotate
    board['hands']['North'] = original_hands['East']
    board['hands']['South'] = original_hands['West']
    board['hands']['East'] = original_hands['South']
    board['hands']['West'] = original_hands['North']
    
    print(f"✅ Board {board_num}: Hands rotated")
    corrected += 1

# Save corrected database
with open('app/www/hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print(f"\n✅ Fixed {corrected} boards")
print("📁 Database saved: app/www/hands_database.json")
print("\n" + "="*70)
