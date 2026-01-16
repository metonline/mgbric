import requests
from bs4 import BeautifulSoup
import re

url = 'https://clubs.vugraph.com/hosgoru/boarddetails.php?event=404377&section=A&pair=1&direction=NS&board=7'
response = requests.get(url, timeout=10)
response.encoding = 'ISO-8859-9'

soup = BeautifulSoup(response.text, 'html.parser')
cells = soup.find_all('td', {'class': 'oyuncu'})

print(f"Found {len(cells)} cells\n")

def get_hands(html):
    """Extract hands from HTML."""
    soup = BeautifulSoup(html, 'html.parser')
    hands = {}
    
    for cell in soup.find_all('td', {'class': 'oyuncu'}):
        name_span = cell.find('span', {'class': 'isim'})
        if name_span:
            name = name_span.get_text().replace('\n', ' ').replace('\r', '').strip()
            html_str = str(cell)
            hand = {}
            
            print(f"\nProcessing {name}:")
            
            for suit_name, suit in [('spades', 'S'), ('hearts', 'H'), ('diamonds', 'D'), ('clubs', 'C')]:
                pattern = rf'<img[^>]*alt="{suit_name}"[^>]*/>[\s]*([A2-9TJKQX]+)'
                m = re.search(pattern, html_str, re.I)
                if m:
                    cards = m.group(1).upper()
                    hand[suit] = cards
                    print(f"  {suit}: {cards}")
                else:
                    print(f"  {suit}: NO MATCH")
            
            print(f"  Total suits: {len(hand)}/4")
            
            if len(hand) == 4:
                hands[['N', 'S', 'E', 'W'][len(hands)]] = hand
    
    return hands if len(hands) == 4 else None

hands = get_hands(response.text)
print(f"\n\nFinal result: {'SUCCESS' if hands else 'FAILURE - Got only ' + str(len(hands) if hands else 0) + ' directions'}")
