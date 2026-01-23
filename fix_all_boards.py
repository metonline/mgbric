#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FIX ALL BOARD HANDS FOR EVENT 405376
Applies all known corrections from vugraph validation
"""
import re

# Known correct hands from vugraph (manually verified from board detail pages)
# Format: board_num: (dealer_num, hand_order_for_dealer)
# The hands are ordered according to how they appear in .lin for each dealer
# Dealer 1 (N): N,E,S
# Dealer 2 (E): E,S,W  
# Dealer 3 (S): S,W,N
# Dealer 4 (W): W,N,E

CORRECTIONS = {
    # Board 1: N deals - we manually fixed this already
    # N: K86.QJT7.AQT.832
    # E: 975.A53.KJ93.J76
    # S: T42.2.8542.KQT54
    # W: (calculated from remaining cards)
    # Current .lin appears correct based on earlier fix
    
    # Board 3: S deals - NEEDS FIX (found wrong)
    # N: J74.KJ6.K85.KT73
    # E: K3.AT953.642.AJ6
    # S: T9652.Q2.J3.Q854
    # W: AQ8.874.AQT97.92
    # For S dealer: order is S,W,N so:
    3: "T9652.Q2.J3.Q854,AQ8.874.AQT97.92,J74.KJ6.K85.KT73",
}

print("Reading event_405376.lin...")
with open('event_405376.lin', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Track which boards we fix
fixes_applied = 0
lin_changes = []

for board_num, correct_hands in CORRECTIONS.items():
    # Find the line for this board
    for i, line in enumerate(lines):
        board_match = re.search(rf'ah\|Board {board_num}\|', line)
        if board_match:
            # Extract current md| part
            md_match = re.search(r'md\|(\d)(.*?)\|sv', line)
            if md_match:
                dealer = md_match.group(1)
                old_hands = md_match.group(2)
                
                # Create new line with corrected hands
                new_line = re.sub(
                    rf'md\|{dealer}{re.escape(old_hands)}\|sv',
                    f'md|{dealer}{correct_hands}|sv',
                    line
                )
                
                lines[i] = new_line
                lin_changes.append({
                    'board': board_num,
                    'old': old_hands,
                    'new': correct_hands
                })
                fixes_applied += 1
                print(f"Board {board_num}: FIXED")
            break

# Write corrected .lin file
if fixes_applied > 0:
    print(f"\nApplying {fixes_applied} fixes to event_405376.lin...")
    with open('event_405376.lin', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("File saved!")
    
    print("\nChanges made:")
    for change in lin_changes:
        print(f"\nBoard {change['board']}:")
        print(f"  Old: {change['old']}")
        print(f"  New: {change['new']}")
else:
    print("No corrections needed!")
