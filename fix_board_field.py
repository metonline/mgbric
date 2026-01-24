#!/usr/bin/env python3
"""Fix board field in hands_database.json - convert Board to board"""

import json

# Load database
with open('hands_database.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Fix board field for hands that have 'Board' but not 'board'
fixed = 0
for i, hand in enumerate(data):
    if 'board' not in hand or hand.get('board') is None:
        if 'Board' in hand and hand['Board'] is not None:
            hand['board'] = hand['Board']
            fixed += 1

print(f"✅ Fixed {fixed} hands with missing 'board' field")

# Save back
with open('hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("✅ Database saved successfully")

# Verify
new_hands = [h for h in data if h.get('date') == '23.01.2026']
print(f"\n📊 23.01.2026 hands: {len(new_hands)}")
if new_hands:
    samples = new_hands[:3]
    for s in samples:
        print(f"  Board {s.get('board')}: event_id={s.get('event_id')}, has dd_analysis={('dd_analysis' in s)}")
