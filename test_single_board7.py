import requests
from bs4 import BeautifulSoup
import re
import json

url = 'https://clubs.vugraph.com/hosgoru/boarddetails.php?event=404377&section=A&pair=1&direction=NS&board=7'
response = requests.get(url, timeout=10)
response.encoding = 'ISO-8859-9'

print(f"Page status: {response.status_code}")
print(f"Page size: {len(response.text)} characters")

soup = BeautifulSoup(response.text, 'html.parser')
cells = soup.find_all('td', {'class': 'oyuncu'})

print(f"Found {len(cells)} oyuncu cells\n")

def get_hands(html):
    """Extract hands from HTML."""
    soup = BeautifulSoup(html, 'html.parser')
    hands = {}
    
    for cell in soup.find_all('td', {'class': 'oyuncu'}):
        if cell.find('span', {'class': 'isim'}):
            html_str = str(cell)
            hand = {}
            
            for suit_name, suit in [('spades', 'S'), ('hearts', 'H'), ('diamonds', 'D'), ('clubs', 'C')]:
                # Match: <img ... alt="suit" ... /> followed by either cards or dash (void)
                m = re.search(rf'<img[^>]*alt="{suit_name}"[^>]*/>[\s]*([A2-9TJKQX-]*)', html_str, re.I)
                if m:
                    cards = m.group(1).strip()
                    # Accept cards (including empty before <br/>) or dash
                    hand[suit] = cards.upper() if cards and cards != '-' else (cards if cards else '')
            
            print(f"Got hand with {len(hand)} suits: {list(hand.keys())}")
            
            if len(hand) == 4:
                hands[['N', 'S', 'E', 'W'][len(hands)]] = hand
    
    return hands if len(hands) == 4 else None

hands = get_hands(response.text)

if hands:
    print(f"\n✓ Successfully parsed hands for all 4 directions")
    output = {
        'N': hands['N'],
        'S': hands['S'],
        'E': hands['E'],
        'W': hands['W']
    }
    print(json.dumps(output, indent=2))
else:
    print(f"\n✗ Failed to parse hands")
