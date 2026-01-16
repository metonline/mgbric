#!/usr/bin/env python3
"""Test fetching boards 27-30 from pair 3."""

import requests
from bs4 import BeautifulSoup
import re

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
                dir = len(hands)
                hands[[' N', 'S', 'E', 'W'][dir]] = hand
    
    return hands if len(hands) == 4 else {}


BASE_URL = 'https://clubs.vugraph.com/hosgoru'

print("Testing fetch from Pair 3...")

pair_num = 3
pair_url = f'{BASE_URL}/pairsummary.php?event=404377&section=A&pair={pair_num}&direction=NS'

response = requests.get(pair_url, timeout=10)
response.encoding = 'ISO-8859-9'

soup = BeautifulSoup(response.text, 'html.parser')

boards = []
for tr in soup.find_all('tr'):
    onclick = tr.get('onclick', '')
    if 'boarddetails.php' in onclick:
        m = re.search(r'board=(\d+)', onclick)
        if m:
            boards.append(int(m.group(1)))

boards = sorted(set(boards))
print(f"Pair 3 has boards: {boards}")

# Test boards 27, 28, 29, 30
for board_num in [27, 28, 29, 30]:
    board_url = f'{BASE_URL}/boarddetails.php?event=404377&section=A&pair={pair_num}&direction=NS&board={board_num}'
    
    print(f"\nBoard {board_num}:")
    print(f"  URL: {board_url}")
    
    response = requests.get(board_url, timeout=10)
    response.encoding = 'ISO-8859-9'
    
    print(f"  Status: {response.status_code}")
    print(f"  Content length: {len(response.text)}")
    
    hands = parse_hands(response.text)
    
    if hands:
        print(f"  ✓ Got hands for {len(hands)} directions")
        for dir in ['N', 'S', 'E', 'W']:
            if dir in hands:
                print(f"    {dir}: OK")
    else:
        print(f"  ✗ No hands found")
        
        # Debug
        soup = BeautifulSoup(response.text, 'html.parser')
        cells = soup.find_all('td', {'class': 'oyuncu'})
        print(f"  Found {len(cells)} oyuncu cells")
