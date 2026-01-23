#!/usr/bin/env python3
"""
Extract hands from vugraph LIN file properly
"""
import json
import re

# Parse LIN file
lin_file = 'event_405376.lin'
hands_from_lin = {}

with open(lin_file, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
            
        # Find md| section which contains hands
        md_match = re.search(r'md\|(\d+)([^|]*)', line)
        if md_match:
            board_num = int(md_match.group(1))
            hands_str = md_match.group(2)
            
            # hands_str format: "K86.QJT7.AQT.832,975.A53.KJ93.J76,T42.2.8542.KQT54"
            # Split by comma - need to handle missing W hand
            hands_parts = hands_str.split(',')
            
            if len(hands_parts) >= 3:
                hands_from_lin[board_num] = {
                    'N': hands_parts[0],
                    'E': hands_parts[1],
                    'S': hands_parts[2],
                    'W': hands_parts[3] if len(hands_parts) > 3 else '',
                }
                print(f"Board {board_num}: N={hands_parts[0]}, E={hands_parts[1]}, S={hands_parts[2]}, W={hands_parts[3] if len(hands_parts) > 3 else '(missing)'}")

print(f"\n✓ Extracted {len(hands_from_lin)} boards from LIN file")
