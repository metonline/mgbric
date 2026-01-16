import requests
from bs4 import BeautifulSoup
import re
import json

url = 'https://clubs.vugraph.com/hosgoru/boarddetails.php?event=404377&section=A&pair=1&direction=NS&board=7'
response = requests.get(url, timeout=10)
soup = BeautifulSoup(response.text, 'html.parser')
cells = soup.find_all('td', class_='oyuncu')

print(f"Found {len(cells)} cells\n")

# Original pattern
pattern_old = r'alt="(spades|hearts|diamonds|clubs)"[^>]*/>([A-KT2-9x]+)'

# New pattern with optional whitespace
pattern_new = r'alt="(spades|hearts|diamonds|clubs)"[^>]*/>\s*([A-KT2-9x]+)'

hands = {
    'N': {'S': '', 'H': '', 'D': '', 'C': ''},
    'S': {'S': '', 'H': '', 'D': '', 'C': ''},
    'E': {'S': '', 'H': '', 'D': '', 'C': ''},
    'W': {'S': '', 'H': '', 'D': '', 'C': ''}
}

directions = ['N', 'S', 'E', 'W']
suit_map = {'spades': 'S', 'hearts': 'H', 'diamonds': 'D', 'clubs': 'C'}

for i, cell in enumerate(cells[:4]):
    direction = directions[i]
    html = str(cell)
    
    print(f"Cell {i} ({direction}):")
    
    # Try old pattern
    old_matches = re.findall(pattern_old, html)
    print(f"  Old pattern matches: {old_matches}")
    
    # Try new pattern
    new_matches = re.findall(pattern_new, html)
    print(f"  New pattern matches: {new_matches}")
    
    # Store with new pattern
    for suit_name, cards in new_matches:
        hands[direction][suit_map[suit_name]] = cards
    
    print()

print("Final hands:")
print(json.dumps(hands, indent=2))
