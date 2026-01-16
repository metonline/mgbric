#!/usr/bin/env python3
"""
Extract suit symbols from the saved boarddetails HTML.
"""

import json
import re
from html.parser import HTMLParser

# Load the current results
with open("board1_final_complete.json", "r", encoding="utf-8") as f:
    results = json.load(f)

# Suit mapping
SUITS = {
    'S': '♠',
    'H': '♥',
    'D': '♦',
    'C': '♣'
}

# Parse the HTML we saved to extract the suit
with open("boarddetails_page.html", "r", encoding="utf-8") as f:
    html = f.read()

# Extract the first fantastic row which is Pair 9's result
# Pattern: <td class="fantastic">4<img src="/images/s.gif" alt="S"></td><td class="fantastic">E</td><td class="fantastic">-1</td>

# Find all fantastic/resultspecial table rows
fantastic_pattern = r'<tr><td class="fantastic">([^<]+)<img src="/images/([sdhcnt]+)\.gif"[^>]*alt="([A-Z]+)"[^>]*></td><td class="fantastic">([EW])</td><td class="fantastic">([^<]+)</td>'

matches = re.findall(fantastic_pattern, html)

print(f"Found {len(matches)} contract rows in HTML")

# First match is Pair 9's result
if matches:
    level, suit_file, suit_alt, declarer, result = matches[0]
    suit_symbol = SUITS.get(suit_alt, "?")
    contract = f"{level}{suit_symbol} ({declarer})"
    print(f"\nPair 9 (EMINE/RABIA) - Board 1:")
    print(f"  Contract: {contract}")
    print(f"  Result: {result}")
    
    # Update Pair 9 in results
    for r in results:
        if r['pair_num'] == '9':
            r['contract'] = contract
            print(f"  ✓ Updated")

# Also try alternative pattern for NT
nt_pattern = r'<td class="fantastic">([3-7]N)</td>'
nt_matches = re.findall(nt_pattern, html)
print(f"\nFound {len(nt_matches)} NT contracts")

# Save updated results
with open("board1_with_suits_final.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("\n✓ Updated Board 1 with suit symbols")
print("✓ Saved to board1_with_suits_final.json")

# Show sample
print("\nSample with suit symbols:")
for r in results[:5]:
    print(f"  {r['pair_names'][:40]:40} | {r['contract']:15} {r['result']:3} | {r['score']:6.2f}%")
