#!/usr/bin/env python3
"""
Create PBN for Dealmaster - WITHOUT Vulnerability tag
"""

import json

with open('app/www/hands_database.json', encoding='utf-8') as f:
    db = json.load(f)

boards = db['events']['hosgoru_04_01_2026']['boards']

def format_hand(hand_dict):
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
    
    # Minimal PBN - without Vulnerability
    pbn_content += f'[Board "{board_num}"]\n'
    pbn_content += f'[Dealer "{dealer}"]\n'
    pbn_content += f'[Deal "N:{n_str} E:{e_str} S:{s_str} W:{w_str}"]\n\n'

with open('hosgoru_dealmaster_minimal.pbn', 'w', encoding='utf-8') as f:
    f.write(pbn_content)

print("✓ Created hosgoru_dealmaster_minimal.pbn")
print("  Without Vulnerability tag")
print("  Try this version if the previous one fails")
