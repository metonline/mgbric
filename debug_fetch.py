import requests
from bs4 import BeautifulSoup
import re

event_id = '405376'
section = 'C'
pair_num = 43
direction = 'NS'
board_num = 1

url = f'https://clubs.vugraph.com/hosgoru/boarddetails.php?event={event_id}&section={section}&pair={pair_num}&direction={direction}&board={board_num}'
print(f"URL: {url}")

resp = requests.get(url, timeout=10)
resp.encoding = 'iso-8859-9'

print(f"Page not found: {'Page not Found' in resp.text}")
print(f"Sayfa Bulunamadı: {'Sayfa Bulunamadı' in resp.text}")

soup = BeautifulSoup(resp.content, 'html.parser')

# h3'ten isimleri al
h3 = soup.find('h3')
if h3:
    h3_text = h3.get_text(strip=True)
    print(f"H3: {h3_text[:80]}")
    match = re.search(r'\d{2}:\d{2}\s*\.\.\.\s*(.+?)\s*\.\.\.\s*Bord', h3_text)
    if match:
        print(f"Pair names: {match.group(1)}")
    else:
        print("Regex did not match!")

results_table = soup.find('table', class_='results')
print(f"Results table found: {results_table is not None}")

if results_table:
    rows = results_table.find_all('tr')
    print(f"Total rows: {len(rows)}")
    
    for i, row in enumerate(rows[:10]):
        cells = row.find_all('td', recursive=False)
        if len(cells) >= 8:
            first_cell_class = cells[0].get('class', [])
            if 'fantastic' in first_cell_class:
                print(f"FOUND FANTASTIC at row {i}")
                print(f"  Cells: {[c.get_text(strip=True)[:15] for c in cells]}")
