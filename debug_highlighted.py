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
    
    # Check for highlighted rows
    for i, row in enumerate(rows):
        row_class = row.get('class', [])
        if row_class:
            print(f"Row {i} class: {row_class}")
        if 'highlighted' in row_class:
            print(f"FOUND HIGHLIGHTED at row {i}")
            cells = row.find_all('td')
            print(f"  Cells count: {len(cells)}")
            for j, cell in enumerate(cells[:10]):
                print(f"  Cell {j}: {cell.get_text(strip=True)[:30]}")
