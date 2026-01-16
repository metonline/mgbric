#!/usr/bin/env python3
"""
Direct hands fetching from Vugraph using HTTP (no Selenium necessary).

Strategy:
1. Parse event page to get pair summary links
2. For each pair, fetch their summary page (has board results table)
3. Extract board details links from pair summary
4. Fetch board details page for hands
5. Parse hands from HTML
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time

EVENT_ID = 404377
BASE_URL = "https://clubs.vugraph.com/hosgoru"

print("\n" + "="*70)
print("DIRECT HTTP HANDS FETCHER")
print("="*70)

# Step 1: Get event page and extract pair links
print("\nStep 1: Getting event page...")

try:
    response = requests.get(f"{BASE_URL}/eventresults.php?event={EVENT_ID}", timeout=10)
    response.encoding = 'ISO-8859-9'  # Turkish encoding
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all links to pairsummary pages
    pair_links = []
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        if 'pairsummary.php' in href and 'event=404377' in href:
            pair_links.append(href)
    
    # Get unique pairs
    unique_pairs = {}
    for href in pair_links:
        match = re.search(r'pair=(\d+)', href)
        if match:
            pair_num = int(match.group(1))
            if pair_num not in unique_pairs:
                unique_pairs[pair_num] = href
    
    pairs = sorted(unique_pairs.items())
    print(f"✓ Found {len(pairs)} pairs")
    
    if pairs:
        print(f"  Sample pairs: {[p[0] for p in pairs[:3]]}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    pairs = []

# Step 2: For each pair, get their board summary
print("\nStep 2: Getting board summaries from each pair...")

boards_data = {}

for pair_num, pair_url in pairs[:3]:  # Test first 3 pairs
    try:
        print(f"\n  Pair {pair_num}...", end="")
        
        # Ensure URL is absolute
        if not pair_url.startswith('http'):
            pair_url = f"{BASE_URL}/{pair_url}"
        
        response = requests.get(pair_url, timeout=10)
        response.encoding = 'ISO-8859-9'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find board links (boarddetails.php)
        board_links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if 'boarddetails.php' in href:
                board_links.append(href)
        
        # Also extract from the table
        tables = soup.find_all('table')
        print(f" found {len(tables)} tables", end="")
        
        # Usually board results are in a table
        if tables:
            # Look for table with board information
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows:
                    cells = row.find_all('td')
                    if cells:
                        # First cell usually has board number
                        first_cell = cells[0].get_text(strip=True)
                        
                        if first_cell.isdigit():
                            board_num = int(first_cell)
                            
                            # Look for link in this row
                            row_link = row.find('a', href=True)
                            if row_link:
                                board_url = row_link.get('href', '')
                                
                                if 'boarddetails' in board_url:
                                    if not board_url.startswith('http'):
                                        board_url = f"{BASE_URL}/{board_url}"
                                    
                                    if board_num not in boards_data:
                                        boards_data[board_num] = {
                                            'url': board_url,
                                            'pair': pair_num,
                                            'sources': []
                                        }
                                    
                                    boards_data[board_num]['sources'].append(pair_num)
        
        print(f", boards: {len([k for k, v in boards_data.items() if pair_num in v['sources']])}")
    
    except Exception as e:
        print(f" ✗ {e}")

print(f"\n✓ Found {len(boards_data)} unique boards")

# Step 3: Fetch hands from board details pages
print("\nStep 3: Fetching hands from board details pages...")

hands_by_board = {}

for board_num, board_info in sorted(boards_data.items())[:3]:  # Test first 3
    try:
        print(f"\n  Board {board_num} (Pair {board_info['pair']})...", end="")
        
        response = requests.get(board_info['url'], timeout=10)
        response.encoding = 'ISO-8859-9'
        
        page_text = response.text
        soup = BeautifulSoup(page_text, 'html.parser')
        
        # Get all text from page
        text = soup.get_text('\n')
        
        print(f" page: {len(text)} chars", end="")
        
        # Look for player names and hands
        lines = text.split('\n')
        
        hands = {}
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Look for compass point names
            compass = None
            if line.upper().startswith('NORTH'):
                compass = 'N'
            elif line.upper().startswith('SOUTH'):
                compass = 'S'
            elif line.upper().startswith('EAST'):
                compass = 'E'
            elif line.upper().startswith('WEST'):
                compass = 'W'
            
            if compass:
                # Look at following lines for hand data
                for j in range(i, min(i+5, len(lines))):
                    next_line = lines[j].strip()
                    
                    # Look for suit indicators
                    if any(suit in next_line for suit in ['S:', 'H:', 'D:', 'C:']):
                        # Try to parse hand
                        hand_dict = {}
                        
                        # Look for pattern: S:xxx H:xxx D:xxx C:xxx
                        pattern = r'([SHDC]):([A2-9TJKQa2-9tjkq]+)'
                        matches = re.findall(pattern, next_line, re.IGNORECASE)
                        
                        if matches:
                            for suit, cards in matches:
                                hand_dict[suit.upper()] = cards.upper()
                            
                            if hand_dict:
                                hands[compass] = hand_dict
                                print(f" {compass}", end="")
                                break
        
        if hands:
            hands_by_board[board_num] = hands
            print(f" ✓ Found {len(hands)} hands")
        else:
            print(f" - No hands found")
            # Show sample of page
            print(f"      Sample text: {text[:300]}")
    
    except Exception as e:
        print(f" ✗ {e}")

# Summary
print("\n" + "="*70)
print("RESULT")
print("="*70)

print(f"\n✓ Successfully fetched hands from {len(hands_by_board)} boards")

for board_num, hands in hands_by_board.items():
    print(f"\n  Board {board_num}:")
    for compass, cards in hands.items():
        card_count = sum(len(v) for v in cards.values())
        print(f"    {compass}: {card_count} cards - {cards}")

print("\n" + "="*70 + "\n")
