import requests
from bs4 import BeautifulSoup

event_url = 'https://clubs.vugraph.com/hosgoru/eventresults.php?event=405376'
resp = requests.get(event_url, timeout=10)
resp.encoding = 'iso-8859-9'
soup = BeautifulSoup(resp.content, 'html.parser')

# 2. tabloyu incele
tables = soup.find_all('table')
if len(tables) >= 2:
    table = tables[1]
    rows = table.find_all('tr')
    print(f"Total rows: {len(rows)}")
    
    # İlk birkaç satır
    for i, row in enumerate(rows[:8]):
        cells = row.find_all(['td', 'th'])
        texts = [c.get_text(strip=True)[:15] for c in cells]
        print(f"Row {i}: {texts}")
