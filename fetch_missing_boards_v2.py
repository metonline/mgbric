#!/usr/bin/env python3
"""Fetch missing boards 7, 9, 17, 19 from the best pairs and add to database."""

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
                m = re.search(rf'<img[^>]*alt="{suit_name}"[^>]*/>[\s]*([A2-9TJKQX-]*)', html_str, re.I)
                if m:
                    cards = m.group(1).strip()
                    hand[suit] = cards.upper() if cards and cards != '-' else (cards if cards else '')
            
            if len(hand) == 4:
                hands[['N', 'S', 'E', 'W'][len(hands)]] = hand
    
    return hands if len(hands) == 4 else None

# Load existing hands
with open('hands_database_fetched.json', 'r') as f:
    boards = json.load(f)

# Convert keys to int for comparison
boards = {int(k): v for k, v in boards.items()}

missing = [7, 9, 17, 19]
print(f"Currently have {len(boards)} boards")
print(f"Missing boards: {missing}\n")

# For each missing board, try to fetch from different pairs
fetch_attempts = {
    7: [1, 2, 3, 4, 7, 8, 9],
    9: [1, 2, 3, 4, 5, 8, 9],
    17: [1, 2, 3, 4, 5, 6, 7, 8],
    19: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13, 14, 15, 21, 22, 23, 24, 25, 30, 31, 33, 35]
}

for board_num in missing:
    print(f"Board {board_num}:")
    found = False
    
    for pair_num in fetch_attempts.get(board_num, [1, 2, 3]):
        if found:
            break
            
        try:
            direction = 'NS' if pair_num < 20 else 'EW'
            url = f"{BASE_URL}/boarddetails.php?event={EVENT_ID}&section=A&pair={pair_num}&direction={direction}&board={board_num}"
            
            response = requests.get(url, timeout=10)
            response.encoding = 'ISO-8859-9'
            
            hands = get_hands(response.text)
            
            if hands:
                boards[board_num] = hands
                print(f"  ✓ Got from Pair {pair_num}")
                found = True
            else:
                print(f"  ✗ Pair {pair_num}: No hands parsed")
            
            time.sleep(0.1)
        
        except Exception as e:
            print(f"  ✗ Pair {pair_num}: {e}")
    
    if not found:
        print(f"  ✗ Failed to fetch from any pair")

print(f"\nFinal count: {len(boards)} boards")
print(f"Board list: {sorted(boards.keys())}")

# Save
output = {str(b): boards[b] for b in sorted(boards.keys())}
with open('hands_database_fetched.json', 'w') as f:
    json.dump(output, f, indent=2)

print("✓ Saved to hands_database_fetched.json")
