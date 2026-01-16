#!/usr/bin/env python3
"""
Extract pair links from event page where links are in onclick attributes.
"""

import requests
from bs4 import BeautifulSoup
import re

EVENT_ID = 404377
BASE_URL = "https://clubs.vugraph.com/hosgoru"

print("\n" + "="*70)
print("EXTRACTING PAIR LINKS FROM EVENT PAGE")
print("="*70)

# Get event page
response = requests.get(f"{BASE_URL}/eventresults.php?event={EVENT_ID}", timeout=10)
response.encoding = 'ISO-8859-9'

soup = BeautifulSoup(response.text, 'html.parser')

# The link is in onclick attribute of <tr> elements
# Example: onclick="location.href='pairsummary.php?event=404377&amp;section=A&amp;pair=9&amp;direction=NS';"

pair_links = {}

for tr in soup.find_all('tr'):
    onclick = tr.get('onclick', '')
    
    if 'pairsummary.php' in onclick and 'event=404377' in onclick:
        # Extract the URL from onclick
        match = re.search(r"'([^']*pairsummary\.php[^']*)'", onclick)
        
        if match:
            url = match.group(1)
            
            # Unescape &amp;
            url = url.replace('&amp;', '&')
            
            # Extract pair number
            pair_match = re.search(r'pair=(\d+)', url)
            if pair_match:
                pair_num = int(pair_match.group(1))
                pair_links[pair_num] = url
                
print(f"\n✓ Found {len(pair_links)} pair links")

# Show some examples
sorted_pairs = sorted(pair_links.items())[:3]
for pair_num, url in sorted_pairs:
    full_url = url if url.startswith('http') else f"{BASE_URL}/{url}"
    print(f"  Pair {pair_num}: {url}")

# Now fetch the first pair summary page
if pair_links:
    pair_num, pair_url = sorted_pairs[0]
    
    print(f"\n" + "="*70)
    print(f"FETCHING PAIR {pair_num} SUMMARY")
    print("="*70)
    
    # Make URL absolute
    if not pair_url.startswith('http'):
        pair_url = f"{BASE_URL}/{pair_url}"
    
    print(f"\nURL: {pair_url}")
    
    response = requests.get(pair_url, timeout=10)
    response.encoding = 'ISO-8859-9'
    
    print(f"Status: {response.status_code}")
    print(f"Content length: {len(response.text)} chars")
    
    # Save for inspection
    with open('pair_summary_example.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    print(f"✓ Saved to pair_summary_example.html")
    
    # Look for board links
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Look for onclick attributes with boarddetails
    board_links = {}
    for element in soup.find_all(attrs={'onclick': True}):
        onclick = element.get('onclick', '')
        
        if 'boarddetails.php' in onclick:
            match = re.search(r"'([^']*boarddetails\.php[^']*)'", onclick)
            if match:
                url = match.group(1).replace('&amp;', '&')
                
                board_match = re.search(r'board=(\d+)', url)
                if board_match:
                    board_num = int(board_match.group(1))
                    board_links[board_num] = url
    
    print(f"\n✓ Found {len(board_links)} board links in pair summary")
    if board_links:
        sorted_boards = sorted(board_links.items())[:3]
        for board_num, url in sorted_boards:
            print(f"  Board {board_num}: {url}")
    
    # Fetch first board
    if board_links:
        board_num, board_url = sorted(board_links.items())[0]
        
        print(f"\n" + "="*70)
        print(f"FETCHING BOARD {board_num} DETAILS")
        print("="*70)
        
        if not board_url.startswith('http'):
            board_url = f"{BASE_URL}/{board_url}"
        
        print(f"\nURL: {board_url}")
        
        response = requests.get(board_url, timeout=10)
        response.encoding = 'ISO-8859-9'
        
        print(f"Status: {response.status_code}")
        print(f"Content length: {len(response.text)} chars")
        
        # Save for inspection
        with open('board_details_example.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"✓ Saved to board_details_example.html")
        
        # Show first 1000 chars
        print("\n" + "-"*70)
        print("PAGE CONTENT PREVIEW:")
        print("-"*70)
        print(response.text[:1000])
        print("...")

print("\n" + "="*70 + "\n")
