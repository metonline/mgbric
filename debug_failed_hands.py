#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to identify problematic hands
"""

import json
from pathlib import Path

try:
    from endplay.types import Deal, Vul
    from endplay.dds import calc_dd_table
except ImportError:
    print("ERROR: endplay not found")
    exit(1)

HANDS_DB_PATH = Path(__file__).parent / "hands_database.json"

def get_vul_enum(board_num):
    cycle_pos = ((board_num - 1) % 16)
    if cycle_pos in [0, 1]:
        return Vul.none
    elif cycle_pos in [2, 3]:
        return Vul.ns
    elif cycle_pos in [4, 5]:
        return Vul.ew
    else:
        return Vul.both

def get_dealer(board_num):
    dealer_cycle = (board_num - 1) % 4
    dealers = ['N', 'E', 'S', 'W']
    return dealers[dealer_cycle]

def hand_to_pbn(north, east, south, west, dealer='N'):
    if dealer == 'N':
        return f"N:{north} {east} {south} {west}"
    elif dealer == 'E':
        return f"E:{east} {south} {west} {north}"
    elif dealer == 'S':
        return f"S:{south} {west} {north} {east}"
    elif dealer == 'W':
        return f"W:{west} {north} {east} {south}"
    return f"N:{north} {east} {south} {west}"

# Problem boards from previous run
problem_boards = [
    (405278, 5),
    (405278, 9),
    (405278, 14),
    (405278, 15),
    (405278, 19),
    (405315, 5),
    (405315, 11),
    (405315, 14),
    (405315, 26),
    (405315, 29),
    (405445, 2),
    (405445, 11),
    (405445, 16),
    (405445, 18),
    (405445, 19),
]

# Load hands
with open(HANDS_DB_PATH, 'r') as f:
    all_hands = json.load(f)

hands_dict = {}
for hand in all_hands:
    key = f"{hand.get('event')}_{hand.get('board')}"
    hands_dict[key] = hand

print("Analyzing problem boards...\n")

for event_id, board_num in problem_boards:
    key = f"{event_id}_{board_num}"
    hand_data = hands_dict.get(key)
    
    if not hand_data:
        print(f"❌ {key}: Hand not found")
        continue
    
    hands = hand_data.get('hands', {})
    dealer = hand_data.get('dealer', get_dealer(board_num))
    
    # Check hand validity
    issues = []
    all_cards = {}
    
    for player in ['N', 'E', 'S', 'W']:
        hand_str = hands.get(player, '')
        if not hand_str:
            issues.append(f"{player} hand empty")
            continue
        
        # Parse hand
        suits = hand_str.split('.')
        if len(suits) != 4:
            issues.append(f"{player} hand format error: {hand_str}")
            continue
        
        card_count = sum(len(s) for s in suits if s != '-')
        if card_count != 13:
            issues.append(f"{player} has {card_count} cards (not 13)")
        
        # Track cards
        for suit_idx, suit in enumerate(suits):
            for card in suit:
                if card == '-':
                    continue
                card_key = (card, suit_idx, player)
                if card_key in all_cards:
                    issues.append(f"Card {card} in suit {suit_idx} duplicated (also in {all_cards[card_key]})")
                all_cards[card_key] = player
    
    # Try to create Deal
    try:
        pbn = hand_to_pbn(hands['N'], hands['E'], hands['S'], hands['W'], dealer)
        deal = Deal.from_pbn(pbn)
        deal.vul = get_vul_enum(board_num)
        
        # Try DD calculation
        dd = calc_dd_table(deal)
        print(f"✓ {key}: OK (no issues detected)")
    except Exception as e:
        issues.append(f"endplay error: {str(e)[:80]}")
    
    if issues:
        print(f"❌ {key}: {hand_data.get('source', '?')}")
        for issue in issues:
            print(f"   - {issue}")
        print(f"   Hands: N={hands.get('N')}, E={hands.get('E')}, S={hands.get('S')}, W={hands.get('W')}")
        print()
