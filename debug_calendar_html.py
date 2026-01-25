#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug calendar page HTML"""

import requests
from bs4 import BeautifulSoup

url = "https://clubs.vugraph.com/hosgoru/calendar.php?month=1&year=2026"
response = requests.get(url, timeout=10)
response.encoding = 'utf-8'

soup = BeautifulSoup(response.text, 'html.parser')

# Find all links
print("All links with 'event' in href:")
count = 0
for link in soup.find_all('a', href=True):
    href = link['href']
    if 'event' in href:
        text = link.get_text(strip=True)
        print(f"  {href[:70]}")
        print(f"    Text: {text}")
        count += 1
        if count >= 10:
            break

print(f"\nTotal links with 'event': (showing first 10)")

# Check table structure
print("\n\nLooking for date/event structure:")
tables = soup.find_all('table')
print(f"Found {len(tables)} tables")

if tables:
    print("\nFirst table structure (first 50 rows):")
    for row in tables[0].find_all('tr')[:50]:
        cells = row.find_all(['td', 'th'])
        for cell in cells:
            text = cell.get_text(strip=True)[:30]
            if text:
                print(f"  | {text}")
