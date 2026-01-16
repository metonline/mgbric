#!/usr/bin/env python3
"""
Convert DD values in hands_database.json:
1. Convert nested format {'NT': {'N': 6, ...}} to flat format {'NTN': 6, ...}
2. Convert values to tricks format (already in tricks, 6-13 range)
"""

import json
import os

db_path = 'app/www/hands_database.json'

with open(db_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Navigate to the boards
boards = data['events']['hosgoru_04_01_2026']['boards']

converted_count = 0
for board_num_str, board in boards.items():
    if 'dd_analysis' not in board:
        continue
    
    dd = board['dd_analysis']
    
    # Check if nested format (dict within dict) or flat format (all ints)
    is_nested = False
    first_value = next(iter(dd.values())) if dd else None
    if isinstance(first_value, dict):
        is_nested = True
    
    if is_nested:
        # Convert from nested to flat format
        flat_dd = {}
        for denom, players_dict in dd.items():
            for player, tricks in players_dict.items():
                key = f"{denom}{player}"
                # Ensure value is in tricks format (6-13)
                # If it's less than 6, it might be contract level format (0-5)
                if isinstance(tricks, (int, float)):
                    if tricks < 6:
                        flat_dd[key] = int(tricks) + 6  # Convert contract level to tricks
                    else:
                        flat_dd[key] = int(tricks)  # Already in tricks format
        
        board['dd_analysis'] = flat_dd
        converted_count += 1
        print(f"Board {board_num_str}: Converted nested to flat format")
    else:
        # Already flat - check if needs conversion from contract levels to tricks
        has_contract_levels = False
        for key, value in dd.items():
            if isinstance(value, (int, float)) and value < 6:
                has_contract_levels = True
                break
        
        if has_contract_levels:
            for key in dd.keys():
                if isinstance(dd[key], (int, float)) and dd[key] < 6:
                    dd[key] = int(dd[key]) + 6

# Save updated database
with open(db_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\nTotal boards converted: {converted_count}")
print(f"Updated {db_path}")
