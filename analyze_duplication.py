#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check if duplicates are TRULY identical"""

import json
import hashlib

data = json.load(open('hands_database.json', encoding='utf-8'))
h405596 = [d for d in data if d.get('event_id') == 405596]

print(f"Event 405596: {len(h405596)} hands\n")

# Check if they're truly identical by hashing
hashes = {}
for idx, h in enumerate(h405596):
    # Create a hash of the hand data (N, E, S, W, dealer, date)
    key_fields = json.dumps({
        'N': h.get('N'),
        'E': h.get('E'),
        'S': h.get('S'),
        'W': h.get('W'),
        'dealer': h.get('dealer'),
        'date': h.get('date'),
        'board': h.get('board'),
        'event_id': h.get('event_id')
    }, sort_keys=True)
    
    hash_val = hashlib.md5(key_fields.encode()).hexdigest()
    
    if hash_val not in hashes:
        hashes[hash_val] = []
    hashes[hash_val].append(idx)

print(f"Unique hand combinations (by core fields): {len(hashes)}")

# Find boards with duplicates
for hash_val, indices in hashes.items():
    if len(indices) > 1:
        boards = [h405596[i].get('board') for i in indices]
        print(f"\nBoard {boards[0]}: appears {len(indices)} times")
        print(f"  Indices in array: {indices}")
        
        # Show first and last
        h1 = h405596[indices[0]]
        h2 = h405596[indices[-1]]
        
        print(f"  Copy 1 (index {indices[0]}): LIN={('YES' if h1.get('lin_string') else 'NO')}, DD={('YES' if h1.get('dd_analysis') else 'NO')}")
        print(f"  Copy 2 (index {indices[-1]}): LIN={('YES' if h2.get('lin_string') else 'NO')}, DD={('YES' if h2.get('dd_analysis') else 'NO')}")
        
        if h1 == h2:
            print(f"  -> IDENTICAL in ALL fields")
        else:
            print(f"  -> DIFFERENT in some fields")

if len(hashes) == 30:
    print(f"\n✅ Confirmed: Event 405596 has 30 UNIQUE boards, each appearing TWICE")
    print(f"   These are TRUE DUPLICATES that should be removed")
