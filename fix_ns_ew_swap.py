#!/usr/bin/env python3
"""
Fix N/S vs E/W partnership swap for all 30 boards
Pattern: N↔W, S↔E (swap the partnerships)
"""

import json

# Load database
with open('app/www/hands_database.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

boards = db['events']['hosgoru_04_01_2026']['boards']

print("\n" + "="*70)
print("FIXING N/S vs E/W PARTNERSHIP SWAP FOR ALL 30 BOARDS".center(70))
print("="*70)

corrected = 0

for board_num in range(1, 31):
    board_key = str(board_num)
    if board_key not in boards:
        continue
    
    board = boards[board_key]
    hands = board['hands']
    
    # Store original hands
    original_hands = {
        'North': hands['North'].copy(),
        'South': hands['South'].copy(),
        'East': hands['East'].copy(),
        'West': hands['West'].copy(),
    }
    
    # Swap partnerships: N↔W, S↔E
    board['hands']['North'] = original_hands['West']
    board['hands']['South'] = original_hands['East']
    board['hands']['East'] = original_hands['South']
    board['hands']['West'] = original_hands['North']
    
    print(f"✅ Board {board_num}: N/S ↔ E/W partnerships swapped")
    corrected += 1

# Save corrected database
with open('app/www/hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print(f"\n✅ Fixed {corrected} boards")
print("📁 Database saved: app/www/hands_database.json")
print("\n" + "="*70)
