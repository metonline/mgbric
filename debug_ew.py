import requests
from bs4 import BeautifulSoup

url = 'https://clubs.vugraph.com/hosgoru/boarddetails.php?event=405315&section=A&pair=1&direction=NS&board=1'
r = requests.get(url, timeout=10)
r.encoding = 'iso-8859-9'
soup = BeautifulSoup(r.content, 'html.parser')
table = soup.find('table', class_='results')

if table:
    rows = table.find_all('tr')
    print(f"Total rows: {len(rows)}")
    
    # Header row
    header = rows[0] if rows else None
    if header:
        ths = header.find_all('th')
        print(f"\nHeader ({len(ths)} columns):")
        for i, th in enumerate(ths):
            print(f"  Col {i}: {th.get_text(strip=True)}")
    
    # Find highlighted row
    for idx, row in enumerate(rows[1:], 1):
        if 'highlighted' in row.get('class', []):
            cells = row.find_all('td')
            print(f"\nHighlighted row {idx} ({len(cells)} cells):")
            for i, cell in enumerate(cells):
                text = cell.get_text(strip=True)
                img = cell.find('img')
                if img:
                    print(f"  Cell {i}: [IMG] {img.get('alt', 'no-alt')}")
                else:
                    print(f"  Cell {i}: '{text}'")
            break
else:
    print("No table found")
