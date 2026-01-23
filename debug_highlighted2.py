import requests
from bs4 import BeautifulSoup

url = 'https://clubs.vugraph.com/hosgoru/boarddetails.php?event=405376&section=C&pair=43&direction=NS&board=1'
resp = requests.get(url, timeout=10)
resp.encoding = 'iso-8859-9'

# HTML'de highlighted var mı?
print("'highlighted' in HTML:", 'highlighted' in resp.text)
print("'Highlighted' in HTML:", 'Highlighted' in resp.text)

# class içeren tüm tr'leri listele
soup = BeautifulSoup(resp.content, 'html.parser')
results_table = soup.find('table', class_='results')
if results_table:
    for i, row in enumerate(results_table.find_all('tr')):
        cls = row.get('class')
        if cls:
            cells = row.find_all('td')
            print(f"Row {i} class={cls}, cells={len(cells)}")
            if cells:
                print(f"  First cells: {[c.get_text(strip=True)[:15] for c in cells[:4]]}")
