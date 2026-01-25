import requests
from bs4 import BeautifulSoup

url = 'https://clubs.vugraph.com/hosgoru/calendar.php?month=1&year=2026'
r = requests.get(url, timeout=10)
r.encoding = 'utf-8'
soup = BeautifulSoup(r.text, 'html.parser')

table = soup.find('table')
if table:
    rows = table.find_all('tr')
    print(f"Total rows: {len(rows)}")
    for i, row in enumerate(rows[:5]):  # Show first 5 rows
        cells = row.find_all('td')
        print(f"\nRow {i}: {len(cells)} cells")
        for j, cell in enumerate(cells[:3]):  # Show first 3 cells
            text = cell.get_text()[:100]
            links_count = len(cell.find_all('a'))
            print(f"  Cell {j}: text='{text}' links={links_count}")
