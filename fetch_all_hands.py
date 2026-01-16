#!/usr/bin/env python3
"""
Complete Vugraph hands fetcher - fetches all 30 boards from all pairs.
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time

EVENT_ID = 404377
BASE_URL = "https://clubs.vugraph.com/hosgoru"


def parse_hands(html):
    """Extract 4 hands from board detail page HTML."""
    soup = BeautifulSoup(html, 'html.parser')
    hands = {}
    
    for cell in soup.find_all('td', {'class': 'oyuncu'}):
        if cell.find('span', {'class': 'isim'}):
            html_str = str(cell)
            hand = {}
            
            for suit_name, suit in [('spades', 'S'), ('hearts', 'H'), ('diamonds', 'D'), ('clubs', 'C')]:
                m = re.search(rf'alt="{suit_name}"[^>]*/>([A2-9TJKQ]+)', html_str, re.I)
                if m:
                    hand[suit] = m.group(1).upper()
            
            if len(hand) == 4:
                dir_idx = len(hands)
                hands[['N', 'S', 'E', 'W'][dir_idx]] = hand
    
    return hands if len(hands) == 4 else {}


print("\n" + "="*70)
print("VUGRAPH COMPLETE HANDS FETCHER")
print("="*70)

# Get event page
print("\nFetching event results...")
response = requests.get(f"{BASE_URL}/eventresults.php?event={EVENT_ID}", timeout=10)
response.encoding = 'ISO-8859-9'

soup = BeautifulSoup(response.text, 'html.parser')

# Extract pair numbers
pair_nums = []
for tr in soup.find_all('tr'):
    onclick = tr.get('onclick', '')
    if 'pairsummary.php' in onclick:
        m = re.search(r'pair=(\d+)', onclick)
        if m:
            pair_nums.append(int(m.group(1)))

pair_nums = sorted(set(pair_nums))
print(f"Found {len(pair_nums)} pairs: {pair_nums[:5]}...")

# Fetch boards from all pairs
all_hands = {}

for pair_idx, pair_num in enumerate(pair_nums):
    # Determine direction
    direction = 'NS' if pair_num < 20 else 'EW'
    
    pair_url = f"{BASE_URL}/pairsummary.php?event={EVENT_ID}&section=A&pair={pair_num}&direction={direction}"
    
    try:
        response = requests.get(pair_url, timeout=10)
        response.encoding = 'ISO-8859-9'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract board numbers from onclick attributes
        boards = []
        for tr in soup.find_all('tr'):
            onclick = tr.get('onclick', '')
            if 'boarddetails.php' in onclick:
                m = re.search(r'board=(\d+)', onclick)
                if m:
                    boards.append(int(m.group(1)))
        
        # Fetch hands for each board
        found = 0
        for board_num in boards:
            board_url = f"{BASE_URL}/boarddetails.php?event={EVENT_ID}&section=A&pair={pair_num}&direction={direction}&board={board_num}"
            
            try:
                response = requests.get(board_url, timeout=10)
                response.encoding = 'ISO-8859-9'
                
                hands = parse_hands(response.text)
                
                if hands and board_num not in all_hands:
                    all_hands[board_num] = hands
                    found += 1
                elif hands and board_num in all_hands:
                    # Board already found from another pair
                    pass
                
                time.sleep(0.02)
            except:
                pass
        
        if (pair_idx + 1) % 5 == 0 or pair_idx == len(pair_nums) - 1:
            print(f"  [{pair_idx + 1:2d}/{len(pair_nums)}] Pair {pair_num:2d}: {found:2d} new boards (total: {len(all_hands)})")
    
    except Exception as e:
        print(f"  Pair {pair_num}: ERROR {e}")

print(f"\n✓ Fetched {len(all_hands)} boards")

# Save
output = {str(b): all_hands[b] for b in sorted(all_hands.keys())}

with open('hands_database_fetched.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"✓ Saved to hands_database_fetched.json")

# Show sample
if '1' in output:
    print(f"\nBoard 1 sample:")
    for dir in ['N', 'S', 'E', 'W']:
        if dir in output['1']:
            cards = ' '.join(f"{s}:{c}" for s, c in sorted(output['1'][dir].items()))
            print(f"  {dir}: {cards}")

print("\n" + "="*70 + "\n")
