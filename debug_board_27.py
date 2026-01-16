#!/usr/bin/env python3
"""Debug fetcher to see why boards 27-30 aren't being added."""

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
print("DEBUG FETCHER")
print("="*70)

# Get event page
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

# Fetch boards from all pairs
all_hands = {}

# Focus on pair 3 which has boards 27-30
for pair_num in [1, 3]:  # Test pairs 1 and 3
    direction = 'NS' if pair_num < 20 else 'EW'
    
    pair_url = f"{BASE_URL}/pairsummary.php?event={EVENT_ID}&section=A&pair={pair_num}&direction={direction}"
    
    print(f"\nPair {pair_num}:")
    print(f"  URL: {pair_url}")
    
    try:
        response = requests.get(pair_url, timeout=10)
        response.encoding = 'ISO-8859-9'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract board numbers
        boards = []
        for tr in soup.find_all('tr'):
            onclick = tr.get('onclick', '')
            if 'boarddetails.php' in onclick:
                m = re.search(r'board=(\d+)', onclick)
                if m:
                    boards.append(int(m.group(1)))
        
        boards = sorted(set(boards))
        print(f"  Boards: {boards}")
        
        # Fetch hands for board 27 if available
        if 27 in boards:
            board_num = 27
            board_url = f"{BASE_URL}/boarddetails.php?event={EVENT_ID}&section=A&pair={pair_num}&direction={direction}&board={board_num}"
            
            print(f"  Board 27 test:")
            print(f"    URL: {board_url[:80]}...")
            
            response = requests.get(board_url, timeout=10)
            response.encoding = 'ISO-8859-9'
            
            hands = parse_hands(response.text)
            
            print(f"    Hands parsed: {list(hands.keys())}")
            
            if hands:
                if board_num in all_hands:
                    print(f"    Board 27 ALREADY in all_hands")
                else:
                    all_hands[board_num] = hands
                    print(f"    Board 27 ADDED to all_hands")
            else:
                print(f"    NO HANDS extracted")
    
    except Exception as e:
        print(f"  ERROR: {e}")

print(f"\nFinal all_hands keys: {sorted(all_hands.keys())}")
