#!/usr/bin/env python3
"""Ultra-verbose fetcher to debug why boards aren't being added."""

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
print("ULTRA-VERBOSE FETCHER")
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

# Test just pairs 1 and 3
all_hands = {}

for pair_num in [1, 3]:
    direction = 'NS' if pair_num < 20 else 'EW'
    
    pair_url = f"{BASE_URL}/pairsummary.php?event={EVENT_ID}&section=A&pair={pair_num}&direction={direction}"
    
    print(f"\nPair {pair_num} ({direction}):")
    
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
    
    # Test fetching boards 1, 27
    for board_num in [1, 27] if pair_num == 1 else [27, 28]:
        if board_num not in boards:
            print(f"  Board {board_num}: NOT in this pair")
            continue
        
        board_url = f"{BASE_URL}/boarddetails.php?event={EVENT_ID}&section=A&pair={pair_num}&direction={direction}&board={board_num}"
        
        response = requests.get(board_url, timeout=10)
        response.encoding = 'ISO-8859-9'
        
        hands = parse_hands(response.text)
        
        print(f"  Board {board_num}:")
        print(f"    Hands keys: {list(hands.keys())}")
        print(f"    Hands valid: {hands != {} and len(hands) == 4}")
        print(f"    Already in all_hands: {board_num in all_hands}")
        
        if hands and board_num not in all_hands:
            all_hands[board_num] = hands
            print(f"    ✓ ADDED to all_hands")
        elif hands and board_num in all_hands:
            print(f"    - SKIPPED (already have)")
        else:
            print(f"    ✗ NOT ADDED (hands invalid: {hands})")

print(f"\nFinal all_hands: {sorted(all_hands.keys())}")
