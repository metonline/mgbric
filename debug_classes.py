import requests
from bs4 import BeautifulSoup

# Farklı pair'ler için kontrol
event_id = '405376'
section = 'C'
board = 1

for pair_num in [1, 2, 3, 10, 20, 27]:
    for direction in ['NS', 'EW']:
        url = f'https://clubs.vugraph.com/hosgoru/boarddetails.php?event={event_id}&section={section}&pair={pair_num}&direction={direction}&board={board}'
        resp = requests.get(url, timeout=10)
        resp.encoding = 'iso-8859-9'
        
        if 'Page not Found' in resp.text or 'Sayfa Bulunamadı' in resp.text:
            continue
            
        soup = BeautifulSoup(resp.content, 'html.parser')
        results_table = soup.find('table', class_='results')
        
        if results_table:
            found = False
            for row in results_table.find_all('tr'):
                cells = row.find_all('td', recursive=False)
                if len(cells) >= 8:
                    first_class = cells[0].get('class', [])
                    if first_class:
                        score_col = 4 if direction == 'NS' else 5
                        score = cells[score_col].get_text(strip=True) if not cells[score_col].find('img') else ''
                        if score:
                            print(f"Pair {pair_num} {direction}: class={first_class}, score={score}")
                            found = True
                            break
            if not found:
                print(f"Pair {pair_num} {direction}: No matching row found!")
