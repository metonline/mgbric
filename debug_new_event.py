import requests
from bs4 import BeautifulSoup

url = 'https://clubs.vugraph.com/hosgoru/boarddetails.php?event=405376&section=C&pair=43&direction=NS&board=1'
resp = requests.get(url, timeout=10)
resp.encoding = 'iso-8859-9'
soup = BeautifulSoup(resp.content, 'html.parser')

# h3'ten isimleri al
h3 = soup.find('h3')
if h3:
    print(f"H3: {h3.get_text(strip=True)[:100]}")

# results tablosundaki yapıyı incele
results_table = soup.find('table', class_='results')
if results_table:
    rows = results_table.find_all('tr')
    print(f"\nTotal rows: {len(rows)}")
    
    for i, row in enumerate(rows[:12]):
        cells = row.find_all('td', recursive=False)
        row_class = row.get('class', [])
        
        if cells:
            texts = []
            for j, cell in enumerate(cells[:10]):
                img = cell.find('img')
                if img:
                    texts.append(f"[IMG]")
                else:
                    texts.append(cell.get_text(strip=True)[:12])
            
            highlight = " <-- HIGHLIGHTED" if 'highlighted' in row_class else ""
            print(f"Row {i} ({len(cells)} cells){highlight}: {texts}")
