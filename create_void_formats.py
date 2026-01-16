#!/usr/bin/env python3
"""
Create formats with void suits as "-" instead of empty string
Also create single board test file
"""

import json

with open('app/www/hands_database.json', encoding='utf-8') as f:
    db = json.load(f)

boards = db['events']['hosgoru_04_01_2026']['boards']

def format_hand(hand_dict):
    """Format hand with "-" for voids"""
    s = hand_dict['S'] if hand_dict['S'] else '-'
    h = hand_dict['H'] if hand_dict['H'] else '-'
    d = hand_dict['D'] if hand_dict['D'] else '-'
    c = hand_dict['C'] if hand_dict['C'] else '-'
    return f"{s}.{h}.{d}.{c}"

# Create single board test (Board 1)
test_pbn = open('hosgoru_board1_test.pbn', 'w', encoding='utf-8')
board = boards['1']

n_str = format_hand(board['hands']['North'])
e_str = format_hand(board['hands']['East'])
s_str = format_hand(board['hands']['South'])
w_str = format_hand(board['hands']['West'])

test_pbn.write(f'[Board "1"]\n')
test_pbn.write(f'[Dealer "{board["dealer"]}"]\n')
test_pbn.write(f'[Vulnerability "{board["vulnerability"]}"]\n')
test_pbn.write(f'[Deal "{n_str} {e_str} {s_str} {w_str}"]\n')
test_pbn.close()

# Create full file with "-" for voids
full_pbn = open('hosgoru_boards_with_voids.pbn', 'w', encoding='utf-8')

for board_num in range(1, 31):
    board = boards[str(board_num)]
    
    n_str = format_hand(board['hands']['North'])
    e_str = format_hand(board['hands']['East'])
    s_str = format_hand(board['hands']['South'])
    w_str = format_hand(board['hands']['West'])
    
    full_pbn.write(f'[Board "{board_num}"]\n')
    full_pbn.write(f'[Dealer "{board["dealer"]}"]\n')
    full_pbn.write(f'[Vulnerability "{board["vulnerability"]}"]\n')
    full_pbn.write(f'[Deal "{n_str} {e_str} {s_str} {w_str}"]\n\n')

full_pbn.close()

print("✓ Created files:")
print("  hosgoru_board1_test.pbn - Single board test (try this first)")
print("  hosgoru_boards_with_voids.pbn - All 30 boards with '-' for voids")
print("\nTry the single board test first to check if solver is working.")
