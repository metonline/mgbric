import requests
from bs4 import BeautifulSoup
import re

url = 'https://clubs.vugraph.com/hosgoru/boarddetails.php?event=405315&section=A&pair=1&direction=NS&board=1'
resp = requests.get(url, timeout=10)
resp.encoding = 'iso-8859-9'
soup = BeautifulSoup(resp.content, 'html.parser')

# h3'ten isimleri al
h3 = soup.find('h3')
if h3:
    h3_text = h3.get_text(strip=True)
    print(f"H3: {h3_text[:100]}")
    match = re.search(r'\d{2}:\d{2}\s*\.\.\.\s*(.+?)\s*\.\.\.\s*Bord', h3_text)
    if match:
        print(f"Pair names: {match.group(1)}")

# results tablosundaki satırları incele - iç içe tabloyu göz önünde bulundur  
results_table = soup.find('table', class_='results')
if results_table:
    # İç tabloyu bul - results tablosunun içinde başka bir tablo var
    inner_tables = results_table.find_all('table')
    print(f"\nInner tables: {len(inner_tables)}")
    
    # Tüm row'ları al (nested dahil)
    all_trs = results_table.find_all('tr', recursive=True)
    print(f"All TRs (including nested): {len(all_trs)}")
    
    # İlk birkaç satırı göster
    for i, tr in enumerate(all_trs[:10]):
        tds = tr.find_all('td', recursive=False)  # Sadece doğrudan çocuklar
        if tds:
            texts = [td.get_text(strip=True)[:15] for td in tds[:6]]
            print(f"Row {i}: {len(tds)} cells - {texts}")
