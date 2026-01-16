#!/usr/bin/env python3
"""Debug hand parsing."""

import requests
from bs4 import BeautifulSoup
import re

EVENT_ID = 404377
BASE_URL = "https://clubs.vugraph.com/hosgoru"

# Fetch board 1 details
board_url = f"{BASE_URL}/boarddetails.php?event={EVENT_ID}&section=A&pair=1&direction=NS&board=1"

response = requests.get(board_url, timeout=10)
response.encoding = 'ISO-8859-9'

soup = BeautifulSoup(response.text, 'html.parser')

# Get player cells
player_cells = soup.find_all('td', {'class': 'oyuncu'})

print(f"Found {len(player_cells)} player cells\n")

for idx, cell in enumerate(player_cells):
    print(f"Cell {idx}:")
    
    name = cell.find('span', {'class': 'isim'})
    if name:
        print(f"  Name: {name.get_text()}")
    
    # Get HTML
    html_str = str(cell)
    
    # Look for suit patterns
    print(f"  HTML sample: {html_str[:200]}")
    
    # Test regex patterns
    for suit_name in ['spades', 'hearts', 'diamonds', 'clubs']:
        pattern = rf'alt="{suit_name}"\s*/>\s*([A2-9TJKQ]+)'
        match = re.search(pattern, html_str)
        
        if match:
            cards = match.group(1).upper()
            print(f"    {suit_name[0].upper()}: {cards}")
        else:
            print(f"    {suit_name[0].upper()}: NOT FOUND")
            
            # Try simpler pattern
            if f'alt="{suit_name}"' in html_str:
                print(f"      BUT found alt='{suit_name}'")
                
                # Find what's after
                idx = html_str.find(f'alt="{suit_name}"')
                after = html_str[idx:idx+100]
                print(f"      Context: {after}")
    
    print()
