#!/usr/bin/env python3
"""Test if all hands for 24.01.2026 have complete data"""

import json

data = json.load(open('hands_database.json', 'r', encoding='utf-8'))

# Filter for 24th
hands_24 = [h for h in data if h.get('date') == '24.01.2026']

print("="*70)
print("24.01.2026 HANDS COMPLETENESS CHECK")
print("="*70)
print(f"\nTotal hands on 24th: {len(hands_24)}")

if len(hands_24) > 0:
    print("\nChecking each hand for required fields:")
    complete = 0
    incomplete = []
    
    required_fields = ['N', 'S', 'E', 'W', 'dealer', 'board', 'event_id', 'lin_string']
    
    for i, hand in enumerate(hands_24, 1):
        missing = [f for f in required_fields if f not in hand]
        if not missing:
            complete += 1
        else:
            incomplete.append((i, hand.get('event_id'), hand.get('board'), missing))
    
    print(f"\nComplete hands: {complete}/{len(hands_24)}")
    print(f"Incomplete hands: {len(incomplete)}/{len(hands_24)}")
    
    if incomplete:
        print("\nIncomplete hands:")
        for idx, event, board, missing_fields in incomplete:
            print(f"  Hand {idx} (Event {event}, Board {board}): Missing {missing_fields}")
    
    print(f"\nSample hands:")
    for h in hands_24[:3]:
        print(f"  Event {h.get('event_id')}, Board {h.get('board')}: {h.get('date')}")
        print(f"    N={h.get('N')}")
        print(f"    S={h.get('S')}")
else:
    print("No hands found for 24.01.2026!")

print("\n" + "="*70)
