#!/usr/bin/env python3
"""Check which pairs have which boards."""

import requests
from bs4 import BeautifulSoup
import re

BASE_URL = 'https://clubs.vugraph.com/hosgoru'

# Check pairs for missing boards
missing_boards = [7, 9, 17, 19]

for pair_num in [1, 2, 3, 4, 5, 6]:  # Check first few NS pairs
    try:
        pair_url = f'{BASE_URL}/pairsummary.php?event=404377&section=A&pair={pair_num}&direction=NS'
        
        response = requests.get(pair_url, timeout=10)
        response.encoding = 'ISO-8859-9'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        board_nums = []
        for tr in soup.find_all('tr'):
            onclick = tr.get('onclick', '')
            if 'boarddetails.php' in onclick and f'pair={pair_num}' in onclick:
                board_match = re.search(r'board=(\d+)', onclick)
                if board_match:
                    board_nums.append(int(board_match.group(1)))
        
        has_missing = any(b in board_nums for b in missing_boards)
        if has_missing:
            found_missing = [b for b in board_nums if b in missing_boards]
            print(f"Pair {pair_num}: HAS {found_missing}")
    except:
        pass

print("\nChecking EW pairs...")

for pair_num in [21, 22, 23, 24, 25]:  # Check first few EW pairs
    try:
        pair_url = f'{BASE_URL}/pairsummary.php?event=404377&section=A&pair={pair_num}&direction=EW'
        
        response = requests.get(pair_url, timeout=10)
        response.encoding = 'ISO-8859-9'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        board_nums = []
        for tr in soup.find_all('tr'):
            onclick = tr.get('onclick', '')
            if 'boarddetails.php' in onclick and f'pair={pair_num}' in onclick:
                board_match = re.search(r'board=(\d+)', onclick)
                if board_match:
                    board_nums.append(int(board_match.group(1)))
        
        has_missing = any(b in board_nums for b in missing_boards)
        if has_missing:
            found_missing = [b for b in board_nums if b in missing_boards]
            print(f"Pair {pair_num}: HAS {found_missing}")
    except:
        pass
