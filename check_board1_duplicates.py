#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check for duplicate hands in event 405596"""

import json

db = json.load(open('hands_database.json'))
hands_405596 = [h for h in db if int(h.get('event_id', 0)) == 405596]

print(f"Total hands from event 405596: {len(hands_405596)}\n")

# Check board 1 specifically
board_1_hands = [h for h in hands_405596 if h.get('board') == 1]
print(f"Hands for Board 1: {len(board_1_hands)}")
for i, h in enumerate(board_1_hands):
    print(f"\n  Hand {i+1}:")
    print(f"    N: {h.get('N')}")
    print(f"    E: {h.get('E')}")
    print(f"    S: {h.get('S')}")
    print(f"    W: {h.get('W')}")
    print(f"    Dealer: {h.get('dealer')}")
    print(f"    Date: {h.get('date')}")
    print(f"    Has LIN: {'YES' if h.get('lin_string') else 'NO'}")
    print(f"    Has DD: {'YES' if h.get('dd_analysis') else 'NO'}")

# Check if they're identical
if len(board_1_hands) == 2:
    h1, h2 = board_1_hands[0], board_1_hands[1]
    print(f"\nAre the N/E/S/W distributions identical?")
    print(f"  N same: {h1.get('N') == h2.get('N')}")
    print(f"  E same: {h1.get('E') == h2.get('E')}")
    print(f"  S same: {h1.get('S') == h2.get('S')}")
    print(f"  W same: {h1.get('W') == h2.get('W')}")
