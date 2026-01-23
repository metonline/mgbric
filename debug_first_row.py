import requests
from bs4 import BeautifulSoup
import re

event_id = '405376'
section = 'C'
board = 1

for pair_num in [41, 42, 43, 51, 52]:
    direction = 'NS' if pair_num < 50 else 'EW'
    url = f'https://clubs.vugraph.com/hosgoru/boarddetails.php?event={event_id}&section={section}&pair={pair_num}&direction={direction}&board={board}'
    resp = requests.get(url, timeout=5)
    resp.encoding = 'iso-8859-9'
    
    if 'Page not Found' in resp.text:
        print(f"Pair {pair_num} {direction}: Page not found")
        continue
    
    soup = BeautifulSoup(resp.content, 'html.parser')
    
    # h3'ten isim
    h3 = soup.find('h3')
    pair_names = ""
    if h3:
        h3_text = h3.get_text(strip=True)
        match = re.search(r'\d{2}:\d{2}\s*\.\.\.\s*(.+?)\s*\.\.\.\s*Bord', h3_text)
        if match:
            pair_names = match.group(1).strip()[:30]
    
    results_table = soup.find('table', class_='results')
    if results_table:
        for row in results_table.find_all('tr'):
            cells = row.find_all('td', recursive=False)
            if len(cells) >= 8:
                contract = cells[0].get_text(strip=True)
                if not contract:
                    img = cells[0].find('img')
                    if img and img.get('alt'):
                        contract = img.get('alt')
                
                if contract:
                    score_col = 4 if direction == 'NS' else 5
                    pct_col = 6 if direction == 'NS' else 7
                    
                    score = cells[score_col].get_text(strip=True) if not cells[score_col].find('img') else '[IMG]'
                    pct = cells[pct_col].get_text(strip=True) if not cells[pct_col].find('img') else '[IMG]'
                    
                    print(f"Pair {pair_num} {direction}: {pair_names} | contract={contract} | score={score} | pct={pct}")
                    break
