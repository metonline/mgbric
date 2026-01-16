#!/usr/bin/env python3
"""Debug version of fetcher."""

import requests
from bs4 import BeautifulSoup
import re
import json
import time

EVENT_ID = 404377
BASE_URL = "https://clubs.vugraph.com/hosgoru"

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
            pattern = rf'alt="{suit_name}"[^>]*/>([A2-9TJKQ]+)'
            match = re.search(pattern, html_str, re.IGNORECASE)
            
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

print("\n" + "="*70)
print("DEBUG VUGRAPH FETCHER")
print("="*70)

# Get event page
response = requests.get(f"{BASE_URL}/eventresults.php?event={EVENT_ID}", timeout=10)
response.encoding = 'ISO-8859-9'

soup = BeautifulSoup(response.text, 'html.parser')

pair_links = {}

for tr in soup.find_all('tr'):
    onclick = tr.get('onclick', '')
    
    if 'pairsummary.php' in onclick and f'event={EVENT_ID}' in onclick:
        match = re.search(r"'([^']*pairsummary\.php[^']*)'", onclick)
        
        if match:
            url = match.group(1).replace('&amp;', '&')
            pair_match = re.search(r'pair=(\d+)', url)
            if pair_match:
                pair_num = int(pair_match.group(1))
                pair_links[pair_num] = url

print(f"Found {len(pair_links)} pairs\n")

# Test just pair 2
pair_num = 2
pair_url = pair_links.get(pair_num)

if pair_url:
    print(f"Testing Pair {pair_num}...")
    
    if not pair_url.startswith('http'):
        pair_url = f"{BASE_URL}/{pair_url}"
    
    print(f"URL: {pair_url}")
    
    response = requests.get(pair_url, timeout=10)
    response.encoding = 'ISO-8859-9'
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find board links
    board_nums = []
    for tr in soup.find_all('tr'):
        onclick = tr.get('onclick', '')
        if 'boarddetails.php' in onclick:
            print(f"  Found onclick: {onclick[:80]}...")
            
            if f'pair={pair_num}' in onclick:
                board_match = re.search(r'board=(\d+)', onclick)
                if board_match:
                    board_nums.append(int(board_match.group(1)))
                    print(f"    -> Board {board_match.group(1)}")
            else:
                print(f"    -> BUT pair!={pair_num} in this onclick")
    
    print(f"\nFound {len(board_nums)} boards for pair {pair_num}: {sorted(board_nums)[:5]}...")
