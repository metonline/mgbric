import requests
from bs4 import BeautifulSoup
import re

event_id = '405376'
section = 'C'
board = 1

# Tüm pair'leri tara - 1'den 100'e kadar
ns_pairs = []
ew_pairs = []

for pair_num in range(1, 100):
    for direction in ['NS', 'EW']:
        url = f'https://clubs.vugraph.com/hosgoru/boarddetails.php?event={event_id}&section={section}&pair={pair_num}&direction={direction}&board={board}'
        resp = requests.get(url, timeout=5)
        resp.encoding = 'iso-8859-9'
        
        if 'Page not Found' in resp.text or 'Sayfa Bulunamadı' in resp.text:
            continue
        
        soup = BeautifulSoup(resp.content, 'html.parser')
        h3 = soup.find('h3')
        if h3:
            if direction == 'NS':
                ns_pairs.append(pair_num)
            else:
                ew_pairs.append(pair_num)

print(f"NS pairs: {len(ns_pairs)} - range {min(ns_pairs) if ns_pairs else 0} to {max(ns_pairs) if ns_pairs else 0}")
print(f"EW pairs: {len(ew_pairs)} - range {min(ew_pairs) if ew_pairs else 0} to {max(ew_pairs) if ew_pairs else 0}")
