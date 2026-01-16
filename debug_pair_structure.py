#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re

BASE_URL = "https://clubs.vugraph.com/hosgoru"
pair_url = "https://clubs.vugraph.com/hosgoru/pairsummary.php?event=404377&section=A&pair=1&direction=NS"

print("Fetching pair 1 summary...")
response = requests.get(pair_url, timeout=10)
response.encoding = 'ISO-8859-9'

soup = BeautifulSoup(response.text, 'html.parser')

print("\nLooking for board links...")

# Method 1: Look for onclick in rows
board_nums = []
for tr in soup.find_all('tr'):
    onclick = tr.get('onclick', '')
    if onclick:
        print(f"Found onclick: {onclick[:80]}...")
        
        if 'boarddetails.php' in onclick:
            board_match = re.search(r'board=(\d+)', onclick)
            if board_match:
                board_num = int(board_match.group(1))
                board_nums.append(board_num)
                print(f"  -> Board {board_num}")

print(f"\nTotal boards found: {len(board_nums)}")

# Also try: Look for href in links
print("\nLooking for href links...")
for link in soup.find_all('a', href=True):
    href = link.get('href')
    if 'boarddetails.php' in href:
        print(f"Found href: {href}")
        board_match = re.search(r'board=(\d+)', href)
        if board_match:
            print(f"  -> Board {board_match.group(1)}")
