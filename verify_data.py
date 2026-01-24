#!/usr/bin/env python3
"""Verify DD analysis was added to new hands"""

import json

data = json.load(open('hands_database.json'))
new_hands = [h for h in data if h.get('date') == '23.01.2026']

print(f"✅ Total hands: {len(data)}")
print(f"✅ New hands (23.01.2026): {len(new_hands)}")

if new_hands:
    h = new_hands[0]
    print(f"\n📊 Sample hand (board 1):")
    print(f"  - event_id: {h.get('event_id')}")
    print(f"  - board: {h.get('board')}")
    print(f"  - has dd_analysis: {'dd_analysis' in h}")
    print(f"  - has optimum: {'optimum' in h}")
    print(f"  - has lott: {'lott' in h}")
    if 'optimum' in h and h['optimum']:
        print(f"  - optimum text: {h['optimum'].get('text')}")
    if 'lott' in h and h['lott']:
        print(f"  - LoTT: {h['lott'].get('total_tricks')}")

# Check all have dd_analysis
complete_count = sum(1 for h in new_hands if 'dd_analysis' in h and 'optimum' in h and 'lott' in h)
print(f"\n✅ Hands with complete analysis: {complete_count}/{len(new_hands)}")
