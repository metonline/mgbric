#!/usr/bin/env python3
"""Test fetching hands for pair 1."""

import requests
from bs4 import BeautifulSoup
import re

def parse_hands_from_html(html_text):
    """Parse hands from board details HTML page."""
    soup = BeautifulSoup(html_text, 'html.parser')
    
    hands = {}
    cells = soup.find_all('td', {'class': 'oyuncu'})
    
    for cell in cells:
        name_span = cell.find('span', {'class': 'isim'})
        if not name_span:
            continue
        
        hand_dict = {}
        html_str = str(cell)
        
        for suit_name, suit_symbol in [('spades', 'S'), ('hearts', 'H'), ('diamonds', 'D'), ('clubs', 'C')]:
            pattern = rf'alt="{suit_name}"\s*/>\s*([A2-9TJKQ]+)'
            match = re.search(pattern, html_str)
            
            if match:
                cards = match.group(1).upper()
                hand_dict[suit_symbol] = cards
        
        if len(hand_dict) == 4:
            if 'N' not in hands:
                hands['N'] = hand_dict
            elif 'S' not in hands:
                hands['S'] = hand_dict
            elif 'E' not in hands:
                hands['E'] = hand_dict
            elif 'W' not in hands:
                hands['W'] = hand_dict
    
    return hands if len(hands) == 4 else {}


EVENT_ID = 404377
BASE_URL = "https://clubs.vugraph.com/hosgoru"

print("Testing fetch for Pair 1, Board 1...")

# Pair 1 - NS direction
pair_url = f"{BASE_URL}/pairsummary.php?event={EVENT_ID}&section=A&pair=1&direction=NS"
print(f"\nFetching pair page: {pair_url}")

response = requests.get(pair_url, timeout=10)
response.encoding = 'ISO-8859-9'

soup = BeautifulSoup(response.text, 'html.parser')

# Find board 1 link
board_link_found = False
for tr in soup.find_all('tr'):
    onclick = tr.get('onclick', '')
    
    if 'board=1' in onclick:
        print(f"Found board 1 onclick: {onclick[:100]}")
        
        # Extract full URL
        match = re.search(r"'([^']*)'", onclick)
        if match:
            board_url = match.group(1).replace('&amp;', '&')
            
            if not board_url.startswith('http'):
                board_url = f"{BASE_URL}/{board_url}"
            
            print(f"Board URL: {board_url}")
            
            # Fetch board details
            print("\nFetching board details...")
            response = requests.get(board_url, timeout=10)
            response.encoding = 'ISO-8859-9'
            
            hands = parse_hands_from_html(response.text)
            
            if hands:
                print(f"\n✓ Got hands!")
                for direction in ['N', 'S', 'E', 'W']:
                    if direction in hands:
                        cards_str = ' '.join(f"{s}:{c}" for s, c in sorted(hands[direction].items()))
                        print(f"  {direction}: {cards_str}")
            else:
                print("✗ No hands found")
                print("\nPage sample:")
                soup = BeautifulSoup(response.text, 'html.parser')
                player_cells = soup.find_all('td', {'class': 'oyuncu'})
                print(f"Found {len(player_cells)} player cells")
            
            board_link_found = True
            break

if not board_link_found:
    print("✗ Board 1 link not found")
