import requests
from bs4 import BeautifulSoup

# Event results sayfasını kontrol et
event_url = 'https://clubs.vugraph.com/hosgoru/eventresults.php?event=405376'
resp = requests.get(event_url, timeout=10)
resp.encoding = 'iso-8859-9'
soup = BeautifulSoup(resp.content, 'html.parser')

print("H3:", soup.find('h3').get_text(strip=True)[:80] if soup.find('h3') else "None")

# Tüm tabloları listele
tables = soup.find_all('table')
print(f"\nTotal tables: {len(tables)}")

for i, table in enumerate(tables):
    prev = table.find_previous(['h4', 'h3', 'h2'])
    prev_text = prev.get_text(strip=True)[:50] if prev else "None"
    rows = table.find_all('tr')
    data_rows = [r for r in rows if r.find('td') and len(r.find_all('td')) >= 2]
    print(f"Table {i}: prev='{prev_text}', total_rows={len(rows)}, data_rows={len(data_rows)}")
