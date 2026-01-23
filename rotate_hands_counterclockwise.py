#!/usr/bin/env python3
"""
Rotate hands COUNTERCLOCKWISE one position (N->W, E->N, S->E, W->S)
This matches the correct BBO dealing where dealer determines rotation
"""
import json

# Load current hands
with open('hands_database.json', 'r', encoding='utf-8') as f:
    hands = json.load(f)

print(f"Fixing rotation for {len(hands)} hands...")

# Rotate each hand counterclockwise
for i, hand in enumerate(hands):
    if i % 50 == 0:
        print(f"  Fixed {i}/{len(hands)}...")
    
    # Current positions
    n = hand['N']
    e = hand['E']
    s = hand['S']
    w = hand['W']
    
    # Rotate counterclockwise: N->W, E->N, S->E, W->S
    hand['N'] = e
    hand['E'] = s
    hand['S'] = w
    hand['W'] = n

print(f"✓ Rotated {len(hands)} hands")

# Save
with open('hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(hands, f, ensure_ascii=False, indent=2)

print("✓ Saved hands_database.json")

# Verify
h = [x for x in hands if x['date']=='20.01.2026' and x['board']==1][0]
print()
print("Board 1 - 20.01.2026 verification:")
print(f"N: {h['N']}")
print(f"E: {h['E']}")
print(f"S: {h['S']}")
print(f"W: {h['W']}")
print()
print("Should match:")
print("N: K86.QJT7.AQT.832")
print("E: 975.A53.KJ93.J76")
print("S: T42.2.8542.KQT54")
print("W: AQJ3.K9864.76.A9")
