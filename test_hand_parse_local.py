#!/usr/bin/env python3
"""Test hand parsing with the actual board_details_example.html file."""

from bs4 import BeautifulSoup
import re

# Read the example HTML
with open('board_details_example.html', 'r', encoding='utf-8') as f:
    html_text = f.read()

soup = BeautifulSoup(html_text, 'html.parser')

# Get player cells
cells = soup.find_all('td', {'class': 'oyuncu'})

print(f"Found {len(cells)} player cells\n")

hands_dict = {}

for idx, cell in enumerate(cells):
    print(f"Cell {idx}:")
    
    # Get name
    name_span = cell.find('span', {'class': 'isim'})
    name = name_span.get_text() if name_span else "Unknown"
    print(f"  Name: {name}")
    
    # Get full HTML
    html_str = str(cell)
    
    # Method 1: Simple string search + regex
    print(f"  HTML length: {len(html_str)}")
    
    hand = {}
    
    # Pattern: the suits come after img tags
    suits = [
        ('spades', 'S'),
        ('hearts', 'H'),
        ('diamonds', 'D'),
        ('clubs', 'C')
    ]
    
    for suit_name, suit_symbol in suits:
        # The HTML has variable order of attributes
        # Pattern: any attribute with the suit name, followed eventually by /> and cards
        pattern = rf'alt="{suit_name}"[^>]*/>([A2-9TJKQ]+)'
        match = re.search(pattern, html_str, re.IGNORECASE)
        
        if match:
            cards = match.group(1).upper()
            hand[suit_symbol] = cards
            print(f"    {suit_symbol}: {cards}")
        else:
            print(f"    {suit_symbol}: NO MATCH")
            
            # Debug: find the suit text
            if f'alt="{suit_name}"' in html_str:
                idx_pos = html_str.find(f'alt="{suit_name}"')
                snippet = html_str[idx_pos:idx_pos+50]
                print(f"      Found '{suit_name}' at: {snippet}")
    
    if len(hand) == 4:
        direction = ['N', 'S', 'E', 'W'][idx]
        hands_dict[direction] = hand
        print(f"  ✓ Complete hand for {direction}")
    else:
        print(f"  ✗ Incomplete hand ({len(hand)}/4 suits)")
    
    print()

print("\nFinal hands:")
for direction, cards in hands_dict.items():
    if cards:
        print(f"{direction}: {cards}")
