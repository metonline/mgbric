#!/usr/bin/env python3
"""
Scraper to fetch actual hand data from Vugraph for all boards
Extracts hand data from board detail pages
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

def parse_hand_from_text(text):
    """Parse hand from text like 'spades Q864 hearts J97 diamonds T3 clubs A842'"""
    hand = {'S': '', 'H': '', 'D': '', 'C': ''}
    
    # Normalize text
    text = text.lower().strip()
    
    # Map suit names to symbols
    suit_map = {
        'spade': 'S', 'heart': 'H', 'diamond': 'D', 'club': 'C',
        'spades': 'S', 'hearts': 'H', 'diamonds': 'D', 'clubs': 'C',
        's': 'S', 'h': 'H', 'd': 'D', 'c': 'C'
    }
    
    for suit_name, suit_symbol in suit_map.items():
        # Find pattern like "spades Q864" or "S Q864"
        pattern = rf'{suit_name}[s]?\s+([A-T2-9]+)'
        match = re.search(pattern, text)
        if match:
            hand[suit_symbol] = match.group(1)
    
    return hand

def extract_hands_from_page(board_num, html_content):
    """Extract hand information from board detail page"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Get all text content
    text = soup.get_text()
    
    # Look for the hand display section
    # Usually contains player names and their hands
    
    hands = {
        'North': {},
        'South': {},
        'East': {},
        'West': {}
    }
    
    # Try to find tables with bidding box and hand information
    tables = soup.find_all('table')
    
    for table in tables:
        table_text = table.get_text()
        
        # Look for text containing hand information with suit symbols
        if any(suit in table_text for suit in ['♠', '♥', '♦', '♣', 'spade', 'heart', 'diamond', 'club']):
            # Found potential hand table
            rows = table.find_all('tr')
            cols = table.find_all('td')
            
            # Extract all text from table
            cells_text = [cell.get_text(strip=True) for cell in cols]
            cells_html = [cell.get_text() for cell in cols]
            
            print(f"\nBoard {board_num} - Found hand data in table:")
            for i, cell in enumerate(cells_text[:20]):  # First 20 cells
                print(f"  Cell {i}: {cell[:80]}")
    
    return hands

def fetch_board_details(board_num, pair=PAIR, direction=DIRECTION):
    """Fetch detailed hand information for a specific board"""
    url = f"{BASE_URL}boarddetails.php?event={EVENT_ID}&section={SECTION}&pair={pair}&direction={direction}&board={board_num}"
    
    print(f"Fetching board {board_num}: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            hands = extract_hands_from_page(board_num, response.content)
            return hands
        else:
            print(f"  Error: Status {response.status_code}")
            return None
    
    except Exception as e:
        print(f"  Error: {e}")
        return None

def main():
    print("Starting Vugraph hand data scraper...")
    print(f"Event: {EVENT_ID}, Section: {SECTION}, Pair: {PAIR}, Direction: {DIRECTION}\n")
    
    # Fetch a few boards to test
    for board_num in range(1, 4):
        hands = fetch_board_details(board_num)
        time.sleep(1)  # Be nice to the server

if __name__ == '__main__':
    main()
