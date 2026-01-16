#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
from bs4 import BeautifulSoup

def fetch_and_parse_event_complete(event_id, turnuva_name, tarih):
    """Fetch and parse BOTH NS and EW results for a tournament event"""
    url = f"https://clubs.vugraph.com/hosgoru/eventresults.php?event={event_id}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        records = []
        
        # Find all tables
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        table_idx = 0
        for table in tables:
            # Get the header row to determine direction
            header_row = table.find('tr')
            if not header_row:
                continue
                
            header_text = header_row.get_text(strip=True)
            
            # Skip header tables and identify NS/EW
            if 'Kuzey' in header_text or 'North' in header_text:
                direction = 'NS'
                print(f"Table {table_idx}: NS (Kuzey-Güney)")
            elif 'Doğu' in header_text or 'East' in header_text:
                direction = 'EW'
                print(f"Table {table_idx}: EW (Doğu-Batı)")
            else:
                # Skip if not a results table
                if 'Hoşgörü' in header_text or not header_text:
                    print(f"Table {table_idx}: Skipped (header/decoration)")
                    table_idx += 1
                    continue
                else:
                    # Unknown table, assume it's a continuation
                    print(f"Table {table_idx}: Unknown - {header_text[:50]}")
                    table_idx += 1
                    continue
            
            # Parse data rows (skip header row)
            rows = table.find_all('tr')[1:]
            
            row_count = 0
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 3:
                    try:
                        sira_text = cells[0].get_text(strip=True)
                        pair_text = cells[1].get_text(strip=True)
                        skor_text = cells[2].get_text(strip=True)
                        
                        # Parse sıra
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
                                'Tarih': tarih,
                                'Oyuncu 1': oyuncu1,
                                'Oyuncu 2': oyuncu2,
                                'Skor': skor,
                                'Direction': direction,
                                'Turnuva': turnuva_name,
                                'Link': url
                            }
                            records.append(record)
                            row_count += 1
                    except (ValueError, IndexError) as e:
                        continue
            
            print(f"  Parsed {row_count} records")
            table_idx += 1
        
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
