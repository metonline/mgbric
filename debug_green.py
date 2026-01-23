import requests
from bs4 import BeautifulSoup

url = 'https://clubs.vugraph.com/hosgoru/boarddetails.php?event=405376&section=C&pair=43&direction=NS&board=1'
resp = requests.get(url, timeout=10)
resp.encoding = 'iso-8859-9'
soup = BeautifulSoup(resp.content, 'html.parser')

results_table = soup.find('table', class_='results')
if results_table:
    rows = results_table.find_all('tr')
    print(f"Total rows: {len(rows)}")
    
    for i, row in enumerate(rows[:15]):
        cells = row.find_all('td', recursive=False)
        if cells:
            # Check for any styling that might indicate highlighting
            row_style = row.get('style', '')
            row_bgcolor = row.get('bgcolor', '')
            first_cell_class = cells[0].get('class', [])
            first_cell_bgcolor = cells[0].get('bgcolor', '')
            first_cell_style = cells[0].get('style', '')
            
            # Get first few cell texts
            texts = [c.get_text(strip=True)[:10] for c in cells[:6]]
            
            if row_style or row_bgcolor or first_cell_bgcolor or first_cell_style or first_cell_class:
                print(f"Row {i}: {texts}")
                print(f"  row style='{row_style}' bgcolor='{row_bgcolor}'")
                print(f"  cell0 class={first_cell_class} bgcolor='{first_cell_bgcolor}' style='{first_cell_style}'")
