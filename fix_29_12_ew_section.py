#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
from bs4 import BeautifulSoup

def fetch_and_parse_event_complete(event_id, turnuva_name, tarih):
    """Fetch and parse BOTH NS and EW results from a single table"""
    url = f"https://clubs.vugraph.com/hosgoru/eventresults.php?event={event_id}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        records = []
        current_direction = None
        
        # Find the main results table
        tables = soup.find_all('table', class_='colored')
        
        if not tables:
            print("No 'colored' table found")
            return []
        
        table = tables[0]
        rows = table.find_all('tr')
        
        print(f"Found {len(rows)} rows in results table\n")
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if not cells:
                continue
            
            # Check if this is a direction header row
            if len(cells) == 1:
                text = cells[0].get_text(strip=True)
                if 'Kuzey' in text or 'North' in text:
                    current_direction = 'NS'
                    print(f"Found NS section: {text}")
                elif 'Doğu' in text or 'Bati' in text or 'East' in text:
                    current_direction = 'EW'
                    print(f"Found EW section: {text}")
            
            # Skip header rows (column names)
            elif len(cells) == 3 and ('Sıra' in cells[0].get_text() or 'Sira' in cells[0].get_text()):
                continue
            
            # Parse data row
            elif len(cells) >= 3 and current_direction:
                try:
                    sira_text = cells[0].get_text(strip=True)
                    pair_text = cells[1].get_text(strip=True)
                    skor_text = cells[2].get_text(strip=True)
                    
                    # Try to parse sıra
                    try:
                        sira = int(sira_text)
                    except ValueError:
                        continue
                    
                    # Parse score
                    skor = float(skor_text.replace(',', '.'))
                    
                    # Parse pair
                    pair_parts = pair_text.split(' - ')
                    if len(pair_parts) >= 2:
                        oyuncu1 = pair_parts[0].strip()
                        oyuncu2 = ' - '.join(pair_parts[1:]).strip()
                        
                        record = {
                            'Sıra': sira,
                            'Tarih': tarih,
                            'Oyuncu 1': oyuncu1,
                            'Oyuncu 2': oyuncu2,
                            'Skor': skor,
                            'Direction': current_direction,
                            'Turnuva': turnuva_name,
                            'Link': url
                        }
                        records.append(record)
                except (ValueError, IndexError) as e:
                    continue
        
        return records
    
    except Exception as e:
        print(f"Error fetching event {event_id}: {e}")
        return []

if __name__ == "__main__":
    event_id = 403999
    turnuva_name = "Pazartesi Sonuçları (29-12-2025 14:00)"
    tarih = "29.12.2025"
    
    print(f"Fetching complete data for event {event_id}...")
    print(f"Date: {tarih}\n")
    
    records = fetch_and_parse_event_complete(event_id, turnuva_name, tarih)
    
    print(f"\nTotal records parsed: {len(records)}")
    
    if records:
        # Count by direction
        ns_records = [r for r in records if r.get('Direction') == 'NS']
        ew_records = [r for r in records if r.get('Direction') == 'EW']
        print(f"NS records: {len(ns_records)}")
        print(f"EW records: {len(ew_records)}")
        
        if ns_records:
            print(f"\nSample NS: {ns_records[0]['Oyuncu 1']} - {ns_records[0]['Oyuncu 2']} ({ns_records[0]['Skor']}%)")
        if ew_records:
            print(f"Sample EW: {ew_records[0]['Oyuncu 1']} - {ew_records[0]['Oyuncu 2']} ({ew_records[0]['Skor']}%)")
        
        # Update database
        with open('database.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Remove old 29.12.2025 records
        old_count = len(data)
        data = [r for r in data if r.get('Tarih') != '29.12.2025']
        removed = old_count - len(data)
        print(f"\nRemoved {removed} old 29.12.2025 records")
        
        # Add new records
        data.extend(records)
        
        # Save
        with open('database.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"Database updated: {len(data)} total records")
        
        # Verify
        verify_29_12 = [r for r in data if r.get('Tarih') == '29.12.2025']
        verify_ns = [r for r in verify_29_12 if r.get('Direction') == 'NS']
        verify_ew = [r for r in verify_29_12 if r.get('Direction') == 'EW']
        print(f"Verification: 29.12.2025 has {len(verify_29_12)} total records (NS: {len(verify_ns)}, EW: {len(verify_ew)})")
        print(f"✓ Data fixed!")
