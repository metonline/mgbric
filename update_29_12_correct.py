#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
from bs4 import BeautifulSoup
import re

def fetch_and_parse_event(event_id, turnuva_name):
    """Fetch and parse results for a specific tournament event"""
    url = f"https://clubs.vugraph.com/hosgoru/eventresults.php?event={event_id}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        records = []
        
        # Find all tables (NS and EW results)
        tables = soup.find_all('table')
        
        for table_idx, table in enumerate(tables):
            # Determine if this is NS or EW table
            header = table.find('tr')
            if header:
                header_text = header.get_text(strip=True)
                if 'Kuzey' in header_text or 'North' in header_text:
                    direction = 'NS'
                elif 'Doğu' in header_text or 'East' in header_text:
                    direction = 'EW'
                else:
                    direction = 'NS' if table_idx == 0 else 'EW'
            else:
                direction = 'NS' if table_idx == 0 else 'EW'
            
            rows = table.find_all('tr')[1:]  # Skip header row
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 3:
                    try:
                        sira_text = cells[0].get_text(strip=True)
                        pair_text = cells[1].get_text(strip=True)
                        skor_text = cells[2].get_text(strip=True)
                        
                        # Parse sıra (rank)
                        sira = int(sira_text)
                        
                        # Parse score
                        skor = float(skor_text.replace(',', '.'))
                        
                        # Parse pair
                        pair_parts = pair_text.split(' - ')
                        if len(pair_parts) >= 2:
                            oyuncu1 = pair_parts[0].strip()
                            oyuncu2 = ' - '.join(pair_parts[1:]).strip()
                            
                            record = {
                                'Sıra': sira,
                                'Tarih': '29.12.2025',
                                'Oyuncu 1': oyuncu1,
                                'Oyuncu 2': oyuncu2,
                                'Skor': skor,
                                'Direction': direction,
                                'Turnuva': turnuva_name,
                                'Link': url
                            }
                            records.append(record)
                    except (ValueError, IndexError) as e:
                        print(f"Error parsing row: {e}")
                        continue
        
        print(f"Parsed {len(records)} records from event {event_id}")
        return records
    
    except Exception as e:
        print(f"Error fetching event {event_id}: {e}")
        return []

if __name__ == "__main__":
    event_id = 403999
    turnuva_name = "Pazartesi Sonuçları (29-12-2025 14:00)"
    
    print(f"Fetching data for event {event_id}...")
    records = fetch_and_parse_event(event_id, turnuva_name)
    
    if records:
        print(f"\nTotal records: {len(records)}")
        print(f"Sample record: {json.dumps(records[0], ensure_ascii=False, indent=2)}")
        
        # Now update database
        with open('database.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Remove old 29.12.2025 records
        old_count = len(data)
        data = [r for r in data if r.get('Tarih') != '29.12.2025']
        removed = old_count - len(data)
        print(f"\nRemoved {removed} old 29.12.2025 records")
        
        # Add new records
        data.extend(records)
        
        # Save updated database
        with open('database.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"Database updated: Total records now {len(data)}")
        
        # Verify
        new_records = [r for r in data if r.get('Tarih') == '29.12.2025']
        print(f"Verification: 29.12.2025 now has {len(new_records)} records")
