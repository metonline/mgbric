#!/usr/bin/env python3
"""
Add placeholder DD values to database
This allows the app to work while we figure out the real DD values
Format: all suits assumed to split evenly (N/S get 7, E/W get 6 on average)
You can update these later with correct values
"""

import json

with open('app/www/hands_database.json', encoding='utf-8') as f:
    db = json.load(f)

boards = db['events']['hosgoru_04_01_2026']['boards']

# Add placeholder DD for all boards
for board_num in range(1, 31):
    board = boards[str(board_num)]
    
    # Placeholder: balanced distribution
    # This is just a placeholder - not accurate!
    board['dd_analysis'] = {
        'NT': {'N': 6, 'E': 7, 'S': 6, 'W': 7},
        'S':  {'N': 6, 'E': 7, 'S': 6, 'W': 7},
        'H':  {'N': 6, 'E': 7, 'S': 6, 'W': 7},
        'D':  {'N': 6, 'E': 7, 'S': 6, 'W': 7},
        'C':  {'N': 6, 'E': 7, 'S': 6, 'W': 7}
    }

# Save
with open('app/www/hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print("✓ Added placeholder DD values to all 30 boards")
print("  All values set to: N=6, E=7, S=6, W=7")
print("  These are PLACEHOLDERS - not accurate!")
print("\nTo update with correct values later:")
print("  1. Get DD values from bridge software")
print("  2. Run: python import_dd_from_file.py")
print("  3. Create dd_values.csv or dd_values.txt with real values")
