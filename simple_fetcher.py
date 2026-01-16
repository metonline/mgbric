#!/usr/bin/env python3
"""Simple sequential fetcher - no tricks, just fetch everything."""

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
                # Match: <img ... alt="suit" ... /> followed by either cards or dash (void)
                m = re.search(rf'<img[^>]*alt="{suit_name}"[^>]*/>[\s]*([A2-9TJKQX-]*)', html_str, re.I)
                if m:
                    cards = m.group(1).strip()
                    # Accept cards (including empty before <br/>) or dash
                    hand[suit] = cards.upper() if cards and cards != '-' else (cards if cards else '')
            
            if len(hand) == 4:
                hands[['N', 'S', 'E', 'W'][len(hands)]] = hand
    
    return hands if len(hands) == 4 else None


print("Fetching all hands from Vugraph...\n")

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

boards = {}

for pi, pn in enumerate(pairs):
    direction = 'NS' if pn < 20 else 'EW'
    pair_url = f"{BASE_URL}/pairsummary.php?event={EVENT_ID}&section=A&pair={pn}&direction={direction}"
    
    r = requests.get(pair_url, timeout=10)
    r.encoding = 'ISO-8859-9'
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Get board numbers
    board_nums = []
    for tr in soup.find_all('tr'):
        m = re.search(r'board=(\d+)', tr.get('onclick', ''))
        if m:
            board_nums.append(int(m.group(1)))
    
    board_nums = sorted(set(board_nums))
    
    # Fetch each board
    new_count = 0
    for bn in board_nums:
        board_url = f"{BASE_URL}/boarddetails.php?event={EVENT_ID}&section=A&pair={pn}&direction={direction}&board={bn}"
        
        r = requests.get(board_url, timeout=10)
        r.encoding = 'ISO-8859-9'
        
        hands = get_hands(r.text)
        
        if hands and bn not in boards:
            boards[bn] = hands
            new_count += 1
        
        time.sleep(0.01)
    
    if (pi + 1) % 10 == 0 or pi == len(pairs) - 1:
        print(f"[{pi+1:2d}/{len(pairs)}] Pair {pn:2d}: {new_count:2d} new boards (total: {len(boards)})")

# Save
output = {str(b): boards[b] for b in sorted(boards.keys())}

with open('hands_database_fetched.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\n✓ Fetched {len(boards)} boards")
print(f"✓ Boards: {sorted(boards.keys())}")
print(f"✓ Saved to hands_database_fetched.json\n")
