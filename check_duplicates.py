#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check for duplicate hands in the database"""

import json
from collections import defaultdict

db = json.load(open('hands_database.json'))

print(f"Total hands in database: {len(db)}\n")

# Check for duplicates by (event_id, board)
duplicates_map = defaultdict(list)
seen = {}

for idx, hand in enumerate(db):
    event_id = hand.get('event_id')
    board = hand.get('board')
    key = (event_id, board)
    
    if key in seen:
        duplicates_map[key].append((idx, seen[key]))
    else:
        seen[key] = idx

# Check event 405596 specifically
print("=" * 70)
print("EVENT 405596 (23.01.2026) ANALYSIS")
print("=" * 70)
hands_405596 = [h for h in db if h.get('event_id') == 405596]
print(f"Total hands from event 405596: {len(hands_405596)}\n")

# Group by board
boards_405596 = defaultdict(list)
for hand in hands_405596:
    board = hand.get('board')
    boards_405596[board].append(hand)

print(f"Boards found: {sorted(boards_405596.keys())}\n")

for board in sorted(boards_405596.keys()):
    hands = boards_405596[board]
    if len(hands) > 1:
        print(f"  Board {board}: {len(hands)} DUPLICATES")
        for i, h in enumerate(hands):
            dealer = h.get('dealer', '?')
            date = h.get('date', '?')
            has_lin = 'YES' if h.get('lin_string') else 'NO'
            has_dd = 'YES' if h.get('dd_analysis') else 'NO'
            print(f"    [{i+1}] Dealer: {dealer}, Date: {date}, LIN: {has_lin}, DD: {has_dd}")
    else:
        print(f"  Board {board}: OK (1 hand)")

# Check all duplicates
print("\n" + "=" * 70)
print("ALL DUPLICATES IN DATABASE")
print("=" * 70)

if duplicates_map:
    print(f"Found {len(duplicates_map)} duplicate (event_id, board) pairs:\n")
    for (event_id, board), indices in sorted(duplicates_map.items()):
        print(f"  Event {event_id}, Board {board}: {len(indices) + 1} copies")
        for idx1, idx2 in indices:
            print(f"    - Index {idx1} (newer)")
            print(f"    - Index {idx2} (older)")
else:
    print("No duplicates found!")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
total_duplicates = sum(len(indices) for indices in duplicates_map.values())
print(f"Total duplicate entries to remove: {total_duplicates}")
print(f"After deduplication: {len(db) - total_duplicates} hands")
