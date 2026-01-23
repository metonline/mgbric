import requests
from bs4 import BeautifulSoup
import re

event_id = '405376'
section = 'C'
board = 1

found_count = 0
not_found_count = 0

for pair_num in range(1, 50):
    url = f'https://clubs.vugraph.com/hosgoru/boarddetails.php?event={event_id}&section={section}&pair={pair_num}&direction=NS&board={board}'
    resp = requests.get(url, timeout=5)
    resp.encoding = 'iso-8859-9'
    
    if 'Page not Found' in resp.text or 'Sayfa Bulunamadı' in resp.text:
        not_found_count += 1
        continue
    
    soup = BeautifulSoup(resp.content, 'html.parser')
    
    # h3'ten isim al
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
                first_class = cells[0].get('class', [])
                if first_class:
                    score_ns = cells[4].get_text(strip=True) if not cells[4].find('img') else ''
                    pct_ns = cells[6].get_text(strip=True) if not cells[6].find('img') else ''
                    if score_ns:
                        print(f"Pair {pair_num}: {pair_names} | class={first_class[0]} | score={score_ns} | pct={pct_ns}")
                        found_count += 1
                        break

print(f"\nFound: {found_count}, Not found pages: {not_found_count}")
