import requests
from bs4 import BeautifulSoup

url = 'https://clubs.vugraph.com/hosgoru/boarddetails.php?event=405376&section=C&pair=41&direction=NS&board=1'
resp = requests.get(url, timeout=10)
resp.encoding = 'iso-8859-9'
soup = BeautifulSoup(resp.content, 'html.parser')

# h3 kontrol
h3 = soup.find('h3')
if h3:
    print(f"H3: {h3.get_text(strip=True)[:80]}")

# Tablo satırları
results_table = soup.find('table', class_='results')
if results_table:
    print("\nAll rows with class:")
    for i, row in enumerate(results_table.find_all('tr')[:10]):
        cells = row.find_all('td', recursive=False)
        if len(cells) >= 6:
            first_class = cells[0].get('class', [])
            contract = cells[0].get_text(strip=True)[:10]
            score_ns = cells[4].get_text(strip=True) if len(cells) > 4 and not cells[4].find('img') else '[IMG]'
            print(f"Row {i}: class={first_class}, contract={contract}, NS score={score_ns}")
