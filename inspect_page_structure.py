#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup

event_id = 403999
url = f"https://clubs.vugraph.com/hosgoru/eventresults.php?event={event_id}"

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all section headers (h2, h3, etc)
    headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'strong', 'b'])
    
    print("=== Page Headers and Important Text ===\n")
    for header in headers[:30]:
        text = header.get_text(strip=True)
        if text and len(text) < 100:
            print(f"{header.name}: {text}")
    
    # Check all table headers (first row of each table)
    tables = soup.find_all('table')
    print(f"\n=== Table Headers ===")
    for i, table in enumerate(tables):
        first_row = table.find('tr')
        if first_row:
            cols = first_row.find_all(['th', 'td'])
            if cols:
                texts = [col.get_text(strip=True) for col in cols[:4]]
                print(f"Table {i}: {texts}")

except Exception as e:
    print(f"Error: {e}")
