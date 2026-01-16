#!/usr/bin/env python3
"""
Complete hands fetcher from Vugraph.
Fetches all hands directly from Vugraph website and saves to JSON.
"""

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
        # Check if cell has player name
        name_span = cell.find('span', {'class': 'isim'})
        if not name_span:
            continue
        
        # Parse suits and cards
        hand_dict = {}
        html_str = str(cell)
        
        # Extract cards for each suit from HTML
        # Pattern: <img ... alt="spades" ... /> followed by any non-< characters (cards)
        for suit_name, suit_symbol in [('spades', 'S'), ('hearts', 'H'), ('diamonds', 'D'), ('clubs', 'C')]:
            # Match: <img ... alt="suit" ... /> followed by card characters or void
            # Handles cases where there's whitespace, <br/>, or direct text between /> and cards
            pattern = rf'<img[^>]*alt="{suit_name}"[^>]*/>[\s]*([A2-9TJKQX-]*)'
            match = re.search(pattern, html_str, re.IGNORECASE)
            
            if match:
                cards = match.group(1).strip()
                # Store cards or void (represented as dash or empty)
                if cards or cards == '-':
                    hand_dict[suit_symbol] = cards.upper() if cards and cards != '-' else cards
        
        if len(hand_dict) == 4:  # Has all 4 suits
            # Assign direction based on order in table
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
print("VUGRAPH HANDS FETCHER")
print("="*70)

# Step 1: Extract pair links from event page
print("\nStep 1: Getting pair links...")

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

print(f"✓ Found {len(pair_links)} pairs")

# Step 2: Fetch hands for each board
print("\nStep 2: Fetching hands from boards...")

hands_by_board = {}

for pair_idx, (pair_num, pair_url) in enumerate(sorted(pair_links.items())):
    try:
        if not pair_url.startswith('http'):
            pair_url = f"{BASE_URL}/{pair_url}"
        
        response = requests.get(pair_url, timeout=10)
        response.encoding = 'ISO-8859-9'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find board numbers from table rows with onclick
        board_nums = []
        for tr in soup.find_all('tr'):
            onclick = tr.get('onclick', '')
            if 'boarddetails.php' in onclick and f'pair={pair_num}' in onclick:
                board_match = re.search(r'board=(\d+)', onclick)
                if board_match:
                    board_num = int(board_match.group(1))
                    board_nums.append(board_num)
        
        # Fetch hands for each board
        boards_found = 0
        for board_num in board_nums:
            try:
                # Extract direction from pair URL
                direction_match = re.search(r'direction=(NS|EW)', pair_url)
                direction = direction_match.group(1) if direction_match else 'NS'
                
                board_url = f"{BASE_URL}/boarddetails.php?event={EVENT_ID}&section=A&pair={pair_num}&direction={direction}&board={board_num}"
                
                response = requests.get(board_url, timeout=10)
                response.encoding = 'ISO-8859-9'
                
                hands = parse_hands_from_html(response.text)
                
                if hands and len(hands) == 4:
                    if board_num not in hands_by_board:
                        hands_by_board[board_num] = hands
                        boards_found += 1
                
            except:
                pass
            
            time.sleep(0.03)  # Be nice to server
        
        if (pair_idx + 1) % 10 == 0 or pair_idx == len(pair_links) - 1:
            print(f"  {pair_idx + 1:2d}/{len(pair_links)}: Pair {pair_num:2d} -> {boards_found} boards")
    
    except Exception as e:
        print(f"  Pair {pair_num}: Error - {e}")

print(f"\n✓ Fetched hands for {len(hands_by_board)} boards")

# Step 3: Save to JSON
if hands_by_board:
    print("\nStep 3: Saving to JSON...")
    
    output_data = {}
    for board_num in sorted(hands_by_board.keys()):
        hands = hands_by_board[board_num]
        
        output_data[str(board_num)] = {
            'north': hands.get('N', {}),
            'south': hands.get('S', {}),
            'east': hands.get('E', {}),
            'west': hands.get('W', {})
        }
    
    with open('hands_database_fetched.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved {len(output_data)} boards to hands_database_fetched.json")
    
    # Show sample
    print("\nSample hands (Board 1):")
    if '1' in output_data:
        for direction in ['north', 'south', 'east', 'west']:
            cards = output_data['1'].get(direction, {})
            if cards:
                cards_str = ' '.join(f"{s}:{c}" for s, c in sorted(cards.items()))
                print(f"  {direction.upper()}: {cards_str}")

print("\n" + "="*70 + "\n")
