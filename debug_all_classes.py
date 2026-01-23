import requests
from bs4 import BeautifulSoup

event_id = '405376'
section = 'C'
board = 1

# NS pair 1 için kontrol
url = f'https://clubs.vugraph.com/hosgoru/boarddetails.php?event={event_id}&section={section}&pair=1&direction=NS&board={board}'
resp = requests.get(url, timeout=10)
resp.encoding = 'iso-8859-9'
soup = BeautifulSoup(resp.content, 'html.parser')

results_table = soup.find('table', class_='results')
if results_table:
    print("All row classes with scores:")
    for i, row in enumerate(results_table.find_all('tr')[:15]):
        cells = row.find_all('td', recursive=False)
        if len(cells) >= 8:
            first_class = cells[0].get('class', [])
            score_ns = cells[4].get_text(strip=True) if not cells[4].find('img') else ''
            score_ew = cells[5].get_text(strip=True) if not cells[5].find('img') else ''
            if score_ns or score_ew:
                contract = cells[0].get_text(strip=True)
                print(f"Row {i}: class={first_class}, contract={contract}, NS={score_ns}, EW={score_ew}")
