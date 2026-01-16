import requests
from bs4 import BeautifulSoup

url = 'https://clubs.vugraph.com/hosgoru/boarddetails.php?event=404377&section=A&pair=1&direction=NS&board=7'
response = requests.get(url, timeout=10)
response.encoding = 'ISO-8859-9'

soup = BeautifulSoup(response.text, 'html.parser')
cells = soup.find_all('td', {'class': 'oyuncu'})

print(f"Found {len(cells)} cells\n")

for i, cell in enumerate(cells[:2]):
    print(f"Cell {i}:")
    html_str = str(cell)
    
    # Show first 300 chars
    print(repr(html_str[:400]))
    print()
    
    # Try both patterns
    import re
    
    pattern1 = r'alt="spades"[^>]*/>([A2-9TJKQ]+)'
    pattern2 = r'<img[^>]*alt="spades"[^>]*/>[\s]*([A2-9TJKQX]+)'
    
    m1 = re.search(pattern1, html_str, re.I)
    m2 = re.search(pattern2, html_str, re.I)
    
    print(f"Pattern 1 (old): {m1.group(1) if m1 else 'NO MATCH'}")
    print(f"Pattern 2 (new): {m2.group(1) if m2 else 'NO MATCH'}")
    print()
