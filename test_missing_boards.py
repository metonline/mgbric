#!/usr/bin/env python3
"""Test why boards 7, 9, 17, 19 are missing."""

import requests
from bs4 import BeautifulSoup
import re

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


BASE_URL = "https://clubs.vugraph.com/hosgoru"

print("Testing missing boards from Pair 1...\n")

for board_num in [7, 9, 17, 19]:
    board_url = f"{BASE_URL}/boarddetails.php?event=404377&section=A&pair=1&direction=NS&board={board_num}"
    
    print(f"Board {board_num}:")
    
    r = requests.get(board_url, timeout=10)
    r.encoding = 'ISO-8859-9'
    
    print(f"  Status: {r.status_code}")
    print(f"  Content length: {len(r.text)}")
    
    hands = get_hands(r.text)
    
    if hands:
        print(f"  ✓ Hands parsed: {list(hands.keys())}")
        # Show sample
        for direction in ['N', 'S']:
            if direction in hands:
                cards = ' '.join(f"{s}:{c}" for s, c in sorted(hands[direction].items()))
                print(f"    {direction}: {cards[:50]}...")
    else:
        print(f"  ✗ NO HANDS PARSED")
        
        # Debug
        soup = BeautifulSoup(r.text, 'html.parser')
        cells = soup.find_all('td', {'class': 'oyuncu'})
        print(f"    Found {len(cells)} oyuncu cells")
        
        if cells:
            # Try to debug the first cell
            cell = cells[0]
            html_str = str(cell)
            print(f"    First cell HTML length: {len(html_str)}")
            print(f"    First 200 chars: {html_str[:200]}")
    
    print()
