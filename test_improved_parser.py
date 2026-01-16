#!/usr/bin/env python3
"""Test improved hand parser on specific boards."""

import requests
from bs4 import BeautifulSoup
import re
import json

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
                    # Accept cards or empty string or dash
                    if cards or cards == '-':
                        hand[suit] = cards.upper() if cards and cards != '-' else cards
            
            if len(hand) == 4:
                hands[['N', 'S', 'E', 'W'][len(hands)]] = hand
    
    return hands if len(hands) == 4 else None

print("Testing improved parser on boards 1, 7, 9, 17, 19...\n")

pair = 1
direction = 'NS'

for board in [1, 7, 9, 17, 19]:
    try:
        url = f"{BASE_URL}/boarddetails.php?event={EVENT_ID}&section=A&pair={pair}&direction={direction}&board={board}"
        response = requests.get(url, timeout=10)
        response.encoding = 'ISO-8859-9'
        
        hands = get_hands(response.text)
        
        if hands:
            print(f"✓ Board {board:2d}: Got hands")
            for direction_key in ['N', 'S', 'E', 'W']:
                hand = hands[direction_key]
                cards = ''.join(f"{s}:{c} " for s, c in sorted(hand.items())).strip()
                print(f"    {direction_key}: {cards}")
        else:
            print(f"✗ Board {board:2d}: No hands parsed")
    except Exception as e:
        print(f"✗ Board {board:2d}: {e}")

print("\nDone!")
