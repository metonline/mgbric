import requests
from bs4 import BeautifulSoup

event_url = 'https://clubs.vugraph.com/hosgoru/eventresults.php?event=405376'
resp = requests.get(event_url, timeout=10)
resp.encoding = 'iso-8859-9'
soup = BeautifulSoup(resp.content, 'html.parser')

tables = soup.find_all('table')
if len(tables) >= 2:
    table = tables[1]
    rows = table.find_all('tr')
    print(f"Total rows: {len(rows)}")
    
    ns_count = 0
    ew_count = 0
    in_ns = False
    in_ew = False
    
    for i, row in enumerate(rows):
        cells = row.find_all(['td', 'th'])
        text = row.get_text(strip=True)
        
        if 'Kuzey' in text or 'North' in text:
            print(f"Row {i}: NS START")
            in_ns = True
            in_ew = False
        elif 'Doğu' in text or 'East' in text:
            print(f"Row {i}: EW START (NS count = {ns_count})")
            in_ew = True
            in_ns = False
        elif in_ns and len(cells) >= 2:
            first = cells[0].get_text(strip=True)
            if first.isdigit():
                ns_count += 1
        elif in_ew and len(cells) >= 2:
            first = cells[0].get_text(strip=True)
            if first.isdigit():
                ew_count += 1
    
    print(f"\nFinal: NS={ns_count}, EW={ew_count}")
