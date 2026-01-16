#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract hands from Vugraph pair summary page
"""

import requests
from bs4 import BeautifulSoup
import json
import re

url = 'https://clubs.vugraph.com/hosgoru/pairsummary.php?event=404377&section=A&pair=9&direction=NS'

print("Fetching hands from Vugraph...")
response = requests.get(url, timeout=10)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.content, 'html.parser')

# Find all tables with board information
tables = soup.find_all('table')
print(f"Found {len(tables)} tables")

# Look for tables containing hand data
hands_by_board = {}

for table_idx, table in enumerate(tables):
    # Try to find board number in the table
    text = table.get_text()
    
    # Look for "Board" keyword
    board_match = re.search(r'Board\s+(\d+)', text)
    if board_match:
        board_num = board_match.group(1)
        print(f"\nBoard {board_num} found in table {table_idx}")
        
        # Extract hands from this table
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            row_text = row.get_text()
            
            # Look for hand positions
            for col_idx, col in enumerate(cols):
                col_text = col.get_text().strip()
                
                # Check if this contains hand information
                if any(suit in col_text for suit in ['S:', 'H:', 'D:', 'C:']):
                    print(f"  Found hand data: {col_text[:80]}")
                    
                    # Try to parse the hand
                    # Format might be: S:AK H:Q D:K87 C:AQJ
                    hand = parse_hand(col_text)
                    if hand and len(hand) > 0:
                        # Determine which position (N, S, E, W)
                        # This requires looking at the table structure
                        print(f"    Parsed: {hand}")

def parse_hand(hand_str):
    """Parse hand from various formats"""
    result = {}
    
    # Try format: S:AK H:Q D:K87 C:AQJ
    if ':' in hand_str:
        parts = hand_str.split()
        for part in parts:
            if ':' in part:
                suit, cards = part.split(':')
                if suit in 'SHDC':
                    result[suit] = cards.replace(',', '')
    
    # Try format: SAKQJT98765432
    if not result:
        for suit in 'SHDC':
            idx = hand_str.find(suit)
            if idx >= 0:
                # Extract cards after suit
                cards_start = idx + 1
                cards_end = cards_start
                while cards_end < len(hand_str) and hand_str[cards_end] not in 'SHDC':
                    cards_end += 1
                result[suit] = hand_str[cards_start:cards_end]
    
    return result

# Print all text to analyze structure
print("\n" + "="*70)
print("PAGE STRUCTURE ANALYSIS")
print("="*70)
print(soup.get_text()[:4000])
