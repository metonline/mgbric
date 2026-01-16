#!/usr/bin/env python3
"""Find which pairs have the missing boards and fetch from them."""

import requests
from bs4 import BeautifulSoup
import re
import json
import time

EVENT_ID = 404377
BASE_URL = "https://clubs.vugraph.com/hosgoru"

def get_hands(html):
    """Extract hands from HTML."""
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
                hands[['N', 'S', 'E', 'W'][len(hands)]] = hand
    
    return hands if len(hands) == 4 else None


print("Finding which pairs have missing boards 7, 9, 17, 19...\n")

missing_boards = [7, 9, 17, 19]

# Get event page
r = requests.get(f"{BASE_URL}/eventresults.php?event={EVENT_ID}", timeout=10)
r.encoding = 'ISO-8859-9'

soup = BeautifulSoup(r.text, 'html.parser')

# Get pair nums
pairs = []
for tr in soup.find_all('tr'):
    m = re.search(r'pair=(\d+)', tr.get('onclick', ''))
    if m:
        pairs.append(int(m.group(1)))

pairs = sorted(set(pairs))

# Start with existing data
existing_boards = json.load(open('hands_database_fetched.json'))
boards = {int(k): v for k, v in existing_boards.items()}

print(f"Currently have {len(boards)} boards: {sorted(boards.keys())}\n")

# Find pairs with missing boards
pair_board_map = {}

for pn in pairs:
    direction = 'NS' if pn < 20 else 'EW'
    pair_url = f"{BASE_URL}/pairsummary.php?event={EVENT_ID}&section=A&pair={pn}&direction={direction}"
    
    r = requests.get(pair_url, timeout=10)
    r.encoding = 'ISO-8859-9'
    soup = BeautifulSoup(r.text, 'html.parser')
    
    board_nums = []
    for tr in soup.find_all('tr'):
        m = re.search(r'board=(\d+)', tr.get('onclick', ''))
        if m:
            board_nums.append(int(m.group(1)))
    
    board_nums = sorted(set(board_nums))
    pair_board_map[pn] = board_nums
    
    # Check if this pair has missing boards
    has_missing = [b for b in missing_boards if b in board_nums]
    if has_missing:
        print(f"Pair {pn:2d}: HAS {has_missing}")

print("\nFetching missing boards from pairs that have them...\n")

# Now fetch missing boards from pairs that have them
for bn in missing_boards:
    if bn in boards:
        print(f"Board {bn}: Already have")
        continue
    
    # Find a pair that has this board
    for pn, board_nums in pair_board_map.items():
        if bn in board_nums:
            direction = 'NS' if pn < 20 else 'EW'
            board_url = f"{BASE_URL}/boarddetails.php?event={EVENT_ID}&section=A&pair={pn}&direction={direction}&board={bn}"
            
            r = requests.get(board_url, timeout=10)
            r.encoding = 'ISO-8859-9'
            
            hands = get_hands(r.text)
            
            if hands:
                boards[bn] = hands
                print(f"Board {bn}: ✓ Fetched from Pair {pn:2d}")
                break
            else:
                print(f"Board {bn}: ✗ Failed from Pair {pn:2d}")
            
            time.sleep(0.02)

# Save all boards
output = {str(b): boards[b] for b in sorted(boards.keys())}

with open('hands_database_fetched.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\n✓ Final count: {len(boards)} boards")
print(f"✓ Boards: {sorted(boards.keys())}")
print(f"✓ Saved to hands_database_fetched.json\n")
