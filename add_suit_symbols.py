#!/usr/bin/env python3
"""
Add suit symbols to contracts in board1_final_complete.json
Manually mapping contracts to suit symbols based on Vugraph data.
"""

import json

# Load current results
with open("board1_final_complete.json", "r", encoding="utf-8") as f:
    results = json.load(f)

# Suit symbols
suit_symbols = {
    'S': '♠',
    'H': '♥',
    'D': '♦',
    'C': '♣'
}

# Manual mapping based on what we found during scraping
# From boarddetails pages for Event 404377, Board 1
contract_suits = {
    '9': ('4', 'S'),     # EMINE/RABIA - 4♠ (E)
    '7': ('4', 'S'),     # METE/OYA - 4♠ (E)
    '5': ('3', 'N'),     # PELİN/HAMİT - 3NT (W)
    '8': ('3', 'C'),     # YILMAZ/SERDAR - 3♣ (W)
    '4': ('4', 'S'),     # AYŞE/MUSTAFA - 4♠ (E)
    '10': ('4', 'S'),    # CÜNEYT/SAİME - 4♠ (E)
}

# For now, let's at least do the ones we know
updated = 0
for result in results:
    pair_num = result['pair_num']
    if pair_num in contract_suits:
        level, suit = contract_suits[pair_num]
        if suit == 'N':
            contract = f"{level}N"
        else:
            contract = f"{level}{suit_symbols[suit]}"
        declarer = result['contract'].split('(')[1].rstrip(')')
        result['contract'] = f"{contract} ({declarer})"
        updated += 1
        print(f"Pair {pair_num}: {result['contract']}")

print(f"\n✓ Updated {updated} contracts with suit symbols")

# Save
with open("board1_with_suit_symbols.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("✓ Saved to board1_with_suit_symbols.json")
