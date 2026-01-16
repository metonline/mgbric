#!/usr/bin/env python3
"""
Scraper to extract actual hand data from Vugraph board detail pages
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time

EVENT_ID = "404377"
SECTION = "A"
PAIR = "9"
DIRECTION = "NS"
BASE_URL = "https://clubs.vugraph.com/hosgoru/"

SUIT_SYMBOLS = {
    's.gif': 'S',
    'spades': 'S',
    'h.gif': 'H',
    'hearts': 'H',
    'd.gif': 'D',
    'diamonds': 'D',
    'c.gif': 'C',
    'clubs': 'C'
}

def extract_hands_from_page(html_content):
    """Extract hand information from Vugraph board detail page"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    hands = {
        'North': {'S': '', 'H': '', 'D': '', 'C': ''},
        'South': {'S': '', 'H': '', 'D': '', 'C': ''},
        'East': {'S': '', 'H': '', 'D': '', 'C': ''},
        'West': {'S': '', 'H': '', 'D': '', 'C': ''}
    }
    
    # Find the bridgetable which contains the hands
    bridge_table = soup.find('table', class_='bridgetable')
    if not bridge_table:
        print("  No bridgetable found")
        return None
    
    # Get all cells with oyuncu class (player cells)
    player_cells = bridge_table.find_all('td', class_='oyuncu')
    
    if len(player_cells) < 4:
        print(f"  Only found {len(player_cells)} player cells")
        return None
    
    # Extract from each player cell
    # The order in the HTML is: South, East, North, West
    player_mapping = {
        0: 'South',
        1: 'East',
        2: 'North',
        3: 'West'
    }
    
    for idx, cell in enumerate(player_cells):
        if idx >= 4:
            break
        
        player_name = player_mapping[idx]
        
        # Find all img tags with suit gifs in this cell
        suit_imgs = cell.find_all('img', src=re.compile(r'/(s|h|d|c)\.gif'))
        
        if not suit_imgs or len(suit_imgs) != 4:
            print(f"  {player_name}: Found {len(suit_imgs) if suit_imgs else 0} suit images")
            continue
        
        # Extract cards after each suit image
        for img in suit_imgs:
            # Get the alt attribute to determine suit
            alt_text = img.get('alt', '').lower()
            
            if 'spade' in alt_text:
                suit = 'S'
            elif 'heart' in alt_text:
                suit = 'H'
            elif 'diamond' in alt_text:
                suit = 'D'
            elif 'club' in alt_text:
                suit = 'C'
            else:
                continue
            
            # Get text immediately after the img tag
            next_text = img.next_sibling
            if next_text:
                cards = str(next_text).strip()
                # Remove <br /> tags and newlines
                cards = cards.replace('<br />', '').replace('\n', '').strip()
                hands[player_name][suit] = cards
        
        print(f"{player_name}: S={hands[player_name]['S']} H={hands[player_name]['H']} D={hands[player_name]['D']} C={hands[player_name]['C']}")
    
    return hands

def fetch_board_hands(board_num):
    """Fetch hand data for a specific board"""
    url = f"{BASE_URL}boarddetails.php?event={EVENT_ID}&section={SECTION}&pair={PAIR}&direction={DIRECTION}&board={board_num}"
    
    print(f"\nBoard {board_num}: Fetching...")
    
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            hands = extract_hands_from_page(response.content)
            return hands
        else:
            print(f"  Error: HTTP {response.status_code}")
            return None
    
    except Exception as e:
        print(f"  Error: {e}")
        return None

def main():
    print("Fetching hands from Vugraph...\n")
    
    boards_data = {}
    
    # Fetch first 3 boards as test
    for board_num in range(1, 4):
        hands = fetch_board_hands(board_num)
        if hands:
            boards_data[board_num] = hands
        time.sleep(1)
    
    # Print summary
    print("\n" + "="*60)
    print("Extracted hands summary:")
    for board_num, hands in boards_data.items():
        print(f"\nBoard {board_num}:")
        for player, hand in hands.items():
            print(f"  {player}: S={hand['S']} H={hand['H']} D={hand['D']} C={hand['C']}")

if __name__ == '__main__':
    main()
