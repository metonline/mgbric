#!/usr/bin/env python3
"""
Create multiple format options to test with the solver
"""

import json

with open('app/www/hands_database.json', encoding='utf-8') as f:
    db = json.load(f)

boards = db['events']['hosgoru_04_01_2026']['boards']

# Try different PBN formats

# Format 1: With N:,E:,S:,W: labels (what we have)
pbn1 = open('hosgoru_boards_format1.pbn', 'w', encoding='utf-8')

# Format 2: Without position labels, just 4 hands in order
pbn2 = open('hosgoru_boards_format2.pbn', 'w', encoding='utf-8')

# Format 3: Use "Deal:" tag with just hands space-separated
pbn3 = open('hosgoru_boards_format3.pbn', 'w', encoding='utf-8')

for board_num in range(1, 31):
    board = boards[str(board_num)]
    
    n_hand = board['hands']['North']
    e_hand = board['hands']['East']
    s_hand = board['hands']['South']
    w_hand = board['hands']['West']
    
    n_str = f"{n_hand['S']}.{n_hand['H']}.{n_hand['D']}.{n_hand['C']}"
    e_str = f"{e_hand['S']}.{e_hand['H']}.{e_hand['D']}.{e_hand['C']}"
    s_str = f"{s_hand['S']}.{s_hand['H']}.{s_hand['D']}.{s_hand['C']}"
    w_str = f"{w_hand['S']}.{w_hand['H']}.{w_hand['D']}.{w_hand['C']}"
    
    dealer = board['dealer']
    vuln = board['vulnerability']
    
    # Format 1: With labels (current format)
    pbn1.write(f'[Board "{board_num}"]\n')
    pbn1.write(f'[Dealer "{dealer}"]\n')
    pbn1.write(f'[Vulnerability "{vuln}"]\n')
    pbn1.write(f'[Deal "N:{n_str} E:{e_str} S:{s_str} W:{w_str}"]\n\n')
    
    # Format 2: Without labels
    pbn2.write(f'[Board "{board_num}"]\n')
    pbn2.write(f'[Dealer "{dealer}"]\n')
    pbn2.write(f'[Vulnerability "{vuln}"]\n')
    pbn2.write(f'[Deal "{n_str} {e_str} {s_str} {w_str}"]\n\n')
    
    # Format 3: Simple format
    pbn3.write(f'[Board "{board_num}"]\n')
    pbn3.write(f'[Dealer "{dealer}"]\n')
    pbn3.write(f'[Vulnerability "{vuln}"]\n')
    pbn3.write(f'[Deal "N:{n_str},E:{e_str},S:{s_str},W:{w_str}"]\n\n')

pbn1.close()
pbn2.close()
pbn3.close()

print("✓ Created 3 format variations:")
print("  1. hosgoru_boards_format1.pbn - With N:,E:,S:,W: labels (current)")
print("  2. hosgoru_boards_format2.pbn - Without labels, space-separated")
print("  3. hosgoru_boards_format3.pbn - With commas between hands")
print("\nTry each format with the solver to find which works.")
