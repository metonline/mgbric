#!/usr/bin/env python3
"""Find which pairs have boards 27-30."""

import requests
from bs4 import BeautifulSoup
import re

BASE_URL = 'https://clubs.vugraph.com/hosgoru'

target_boards = [27, 28, 29, 30]

print("Looking for boards 27-30...")

for pair_num in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]:
    try:
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
        
        has_target = any(b in target_boards for b in boards)
        if has_target:
            found = [b for b in boards if b in target_boards]
            print(f"Pair {pair_num:2d} NS: HAS {found}")
    except:
        pass

for pair_num in [21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35]:
    try:
        pair_url = f'{BASE_URL}/pairsummary.php?event=404377&section=A&pair={pair_num}&direction=EW'
        
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
        
        has_target = any(b in target_boards for b in boards)
        if has_target:
            found = [b for b in boards if b in target_boards]
            print(f"Pair {pair_num:2d} EW: HAS {found}")
    except:
        pass
