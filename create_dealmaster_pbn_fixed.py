#!/usr/bin/env python3
"""
Create PBN file for Dealmaster - FIXED vulnerability format
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

def format_vuln(vuln_str):
    """Convert vulnerability to Dealmaster format"""
    vuln_map = {
        "None": "-",
        "N-S": "NS",
        "E-W": "EW",
        "Both": "All"
    }
    return vuln_map.get(vuln_str, vuln_str)

pbn_content = ""

for board_num in range(1, 31):
    board = boards[str(board_num)]
    
    n_str = format_hand(board['hands']['North'])
    e_str = format_hand(board['hands']['East'])
    s_str = format_hand(board['hands']['South'])
    w_str = format_hand(board['hands']['West'])
    
    dealer = board['dealer']
    vuln = format_vuln(board['vulnerability'])
    
    # PBN format for Dealmaster (FIXED)
    pbn_content += f'[Board "{board_num}"]\n'
    pbn_content += f'[Dealer "{dealer}"]\n'
    pbn_content += f'[Vulnerability "{vuln}"]\n'
    pbn_content += f'[Deal "N:{n_str} E:{e_str} S:{s_str} W:{w_str}"]\n\n'

# Write file
with open('hosgoru_dealmaster.pbn', 'w', encoding='utf-8') as f:
    f.write(pbn_content)

print("✓ Fixed hosgoru_dealmaster.pbn")
print("  Vulnerability values: - (None), NS, EW, All")
print("  Ready for Dealmaster")
