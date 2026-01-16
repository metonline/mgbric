#!/usr/bin/env python3
"""
Regenerate LIN file with corrected hands
"""

import json

with open('app/www/hands_database.json', encoding='utf-8') as f:
    db = json.load(f)

boards = db['events']['hosgoru_04_01_2026']['boards']

lin_content = ""

for board_num in range(1, 31):
    board = boards[str(board_num)]
    
    # Get hands
    n_hand = board['hands']['North']
    e_hand = board['hands']['East']
    s_hand = board['hands']['South']
    w_hand = board['hands']['West']
    
    # Format as S.H.D.C for each position
    n_str = f"{n_hand['S']}.{n_hand['H']}.{n_hand['D']}.{n_hand['C']}"
    e_str = f"{e_hand['S']}.{e_hand['H']}.{e_hand['D']}.{e_hand['C']}"
    s_str = f"{s_hand['S']}.{s_hand['H']}.{s_hand['D']}.{s_hand['C']}"
    w_str = f"{w_hand['S']}.{w_hand['H']}.{w_hand['D']}.{w_hand['C']}"
    
    # PBN format
    lin_content += f'[Board "{board_num}"]\n'
    lin_content += f'[Dealer "{board["dealer"]}"]\n'
    lin_content += f'[Vulnerability "{board["vulnerability"]}"]\n'
    lin_content += f'[Deal "N:{n_str} E:{e_str} S:{s_str} W:{w_str}"]\n'
    lin_content += '\n'

# Write to file
with open('hosgoru_boards.lin', 'w', encoding='utf-8') as f:
    f.write(lin_content)

print("✓ LIN file regenerated successfully!")
print(f"  File: hosgoru_boards.lin")
print(f"  Boards: 30")
print(f"  Format: PBN with corrected hands")
