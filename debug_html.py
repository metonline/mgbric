import requests
from bs4 import BeautifulSoup

url = 'https://clubs.vugraph.com/hosgoru/boarddetails.php?event=405315&section=A&pair=1&direction=NS&board=1'
resp = requests.get(url, timeout=10)
resp.encoding = 'iso-8859-9'

# HTML'in bir kısmını göster
print("Looking for 'highlighted' in HTML:")
if 'highlighted' in resp.text:
    idx = resp.text.find('highlighted')
    print(resp.text[max(0, idx-100):idx+200])
else:
    print("'highlighted' NOT found in HTML")
    
# Tüm tabloları listele
soup = BeautifulSoup(resp.content, 'html.parser')
tables = soup.find_all('table')
print(f"\n\nTotal tables: {len(tables)}")
for i, t in enumerate(tables):
    cls = t.get('class', [])
    rows = len(t.find_all('tr'))
    print(f"Table {i}: class={cls}, rows={rows}")
