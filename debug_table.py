import requests
from bs4 import BeautifulSoup

url = 'https://clubs.vugraph.com/hosgoru/boarddetails.php?event=405315&section=A&pair=1&direction=NS&board=1'
resp = requests.get(url, timeout=10)
resp.encoding = 'iso-8859-9'
soup = BeautifulSoup(resp.content, 'html.parser')

results_table = soup.find('table', class_='results')
print("Table found:", results_table is not None)

if results_table:
    rows = results_table.find_all('tr')
    print(f"Total rows: {len(rows)}")
    
    for i, row in enumerate(rows[:5]):  # İlk 5 satır
        cells = row.find_all('td')
        ths = row.find_all('th')
        
        if ths:
            print(f"\nRow {i} (HEADER - {len(ths)} ths):")
            for j, th in enumerate(ths):
                print(f"  TH{j}: {th.get_text(strip=True)[:30]}")
        elif cells:
            print(f"\nRow {i} ({len(cells)} cells, class={row.get('class', [])}):")
            for j, cell in enumerate(cells):
                text = cell.get_text(strip=True)[:30]
                img = cell.find('img')
                if img:
                    print(f"  Cell{j}: [IMG]")
                else:
                    print(f"  Cell{j}: '{text}'")
