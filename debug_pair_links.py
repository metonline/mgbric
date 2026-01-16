#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re

EVENT_ID = 404377
BASE_URL = 'https://clubs.vugraph.com/hosgoru'

response = requests.get(f'{BASE_URL}/eventresults.php?event={EVENT_ID}', timeout=10)
response.encoding = 'ISO-8859-9'

soup = BeautifulSoup(response.text, 'html.parser')

pair_links = {}

for tr in soup.find_all('tr'):
    onclick = tr.get('onclick', '')
    
    if 'pairsummary.php' in onclick and f'event={EVENT_ID}' in onclick:
        match = re.search(r"'([^']*pairsummary\.php[^']*)'", onclick)
        
        if match:
            url = match.group(1).replace('&amp;', '&')
            pair_match = re.search(r'pair=(\d+)', url)
            if pair_match:
                pair_num = int(pair_match.group(1))
                pair_links[pair_num] = url
                print(f"Pair {pair_num}: {url}")

print(f"\nTotal pairs: {len(pair_links)}")
print(f"Pair numbers: {sorted(pair_links.keys())}")
