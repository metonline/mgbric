#!/usr/bin/env python3
"""
Create DLM format file (simpler format for double dummy solver)
DLM format: Board#,Dealer,Vulnerability,Hands
Hands in format: N,E,S,W each as S.H.D.C
"""

import json

with open('app/www/hands_database.json', encoding='utf-8') as f:
    db = json.load(f)

boards = db['events']['hosgoru_04_01_2026']['boards']

# Vulnerability mapping - convert full text to abbreviated
vuln_map = {
    "None": "-",
    "N-S": "NS", 
    "E-W": "EW",
    "Both": "All"
}

dlm_lines = []

for board_num in range(1, 31):
    board = boards[str(board_num)]
    
    dealer = board['dealer']
    vuln = vuln_map.get(board['vulnerability'], board['vulnerability'])
    
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
    
    # DLM format
    line = f"{board_num},{dealer},{vuln},{n_str},{e_str},{s_str},{w_str}"
    dlm_lines.append(line)

# Write to file
with open('hosgoru_boards.dlm', 'w', encoding='utf-8') as f:
    for line in dlm_lines:
        f.write(line + '\n')

print("✓ DLM file created: hosgoru_boards.dlm")
print(f"  Format: Board,Dealer,Vulnerability,N_hand,E_hand,S_hand,W_hand")
print(f"  Boards: 30")
print("\nTry uploading this simpler format to the solver.")
