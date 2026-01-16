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
    
    # Find all tables
    tables = soup.find_all('table')
    print(f"Found {len(tables)} tables\n")
    
    for table_idx, table in enumerate(tables):
        print(f"=== Table {table_idx} ===")
        
        # Get table header
        first_row = table.find('tr')
        if first_row:
            header_text = first_row.get_text(strip=True)
            print(f"Header: {header_text[:100]}")
        
        # Count data rows
        all_rows = table.find_all('tr')
        print(f"Total rows: {len(all_rows)}")
        
        # Show first few data rows
        data_rows = all_rows[1:6]
        for row_idx, row in enumerate(data_rows, 1):
            cells = row.find_all('td')
            if cells:
                cell_texts = [cell.get_text(strip=True)[:30] for cell in cells[:4]]
                print(f"  Row {row_idx}: {cell_texts}")
        print()

except Exception as e:
    print(f"Error: {e}")
