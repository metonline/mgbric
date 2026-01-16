#!/usr/bin/env python3
"""
Create PBN file for Dealmaster DD calculation
Dealmaster expects standard PBN format
"""

import json

with open('app/www/hands_database.json', encoding='utf-8') as f:
    db = json.load(f)

boards = db['events']['hosgoru_04_01_2026']['boards']

def format_hand(hand_dict):
    """Format hand - use - for voids"""
    s = hand_dict['S'] if hand_dict['S'] else '-'
    h = hand_dict['H'] if hand_dict['H'] else '-'
    d = hand_dict['D'] if hand_dict['D'] else '-'
    c = hand_dict['C'] if hand_dict['C'] else '-'
    return f"{s}.{h}.{d}.{c}"

pbn_content = ""

for board_num in range(1, 31):
    board = boards[str(board_num)]
    
    n_str = format_hand(board['hands']['North'])
    e_str = format_hand(board['hands']['East'])
    s_str = format_hand(board['hands']['South'])
    w_str = format_hand(board['hands']['West'])
    
    dealer = board['dealer']
    vuln = board['vulnerability']
    
    # PBN format for Dealmaster
    pbn_content += f'[Board "{board_num}"]\n'
    pbn_content += f'[Dealer "{dealer}"]\n'
    pbn_content += f'[Vulnerability "{vuln}"]\n'
    pbn_content += f'[Deal "N:{n_str} E:{e_str} S:{s_str} W:{w_str}"]\n\n'

# Write file
with open('hosgoru_dealmaster.pbn', 'w', encoding='utf-8') as f:
    f.write(pbn_content)

print("✓ Created hosgoru_dealmaster.pbn")
print("  File ready for Dealmaster")
print("\nSteps:")
print("  1. Open hosgoru_dealmaster.pbn in Dealmaster")
print("  2. Analyze all boards for DD values")
print("  3. Export/save results")
print("  4. Use import_dd_from_dealmaster.py to update database")
