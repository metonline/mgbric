#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HACI KANTARCI - YAŞAR KARATOPRAK (Pair #11, EW direction) के लिए लापता board परिणाम vugraph से चाहिए
Fetch from pairsummary page which shows all boards for a pair
"""

import json
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import time

EVENT_ID = '405376'
PAIR_NUM = 11
DIRECTION = 'EW'
SECTION = 'A'
OUTPUT_FILE = 'board_results.json'
REQUEST_TIMEOUT = 15

def fetch_pair_summary():
    """Fetch pair summary page from vugraph to get all board results for the pair"""
    try:
        url = f'https://clubs.vugraph.com/hosgoru/pairsummary.php?event={EVENT_ID}&section={SECTION}&pair={PAIR_NUM}&direction={DIRECTION}'
        
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.encoding = 'iso-8859-9'
        
        # Page not found kontrolü
        if 'Page not Found' in resp.text or 'Sayfa Bulunamadı' in resp.text:
            return None
        
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # Pair ismini al from h4 tag
        pair_names = ""
        h4 = soup.find('h4')
        if h4:
            h4_text = h4.get_text(strip=True)
            # Format: "HACI KANTARCI - YAŞAR KARATOPRAK Çift Özeti"
            if 'Çift' in h4_text or 'Cift' in h4_text:
                pair_names = h4_text.replace('Çift Özeti', '').replace('Cift Ozeti', '').strip()
        
        if not pair_names:
            print("ERROR: Could not find pair names in summary page")
            return None
        
        # Find the results table (second table on page)
        tables = soup.find_all('table')
        if len(tables) < 2:
            print("ERROR: Could not find results table")
            return None
        
        results_table = tables[1]
        
        rows = results_table.find_all('tr')
        if not rows:
            print("ERROR: No rows in results table")
            return None
        
        # Parse the results - skip header row
        board_results = {}
        
        for row in rows[1:]:  # Skip header
            cells = row.find_all('td')
            if len(cells) < 4:
                continue
            
            try:
                # Column 0: Board number
                board_text = cells[0].get_text(strip=True)
                if not board_text.isdigit():
                    continue
                board_num = int(board_text)
                
                # Column 1: Contract
                contract = cells[1].get_text(strip=True)
                
                # Column 2: Result (e.g., -2, +1)
                result = cells[2].get_text(strip=True)
                
                # Column 3: Score
                score = cells[3].get_text(strip=True)
                
                # Column 4: Percent (if exists)
                percent_text = cells[4].get_text(strip=True) if len(cells) > 4 else '0'
                try:
                    percent = float(percent_text.replace(',', '.')) if percent_text else 0
                except:
                    percent = 0
                
                # Store result
                board_results[board_num] = {
                    'pair_names': pair_names,
                    'direction': DIRECTION,
                    'contract': contract if contract != '-' else '-',
                    'declarer': '-',  # We'll set this later
                    'result': result,
                    'lead': '-',
                    'score': score,
                    'percent': percent
                }
                
                print(f"  Board {board_num}: Contract={contract}, Result={result}, Score={score}, Percent={percent}")
            
            except Exception as e:
                continue
        
        return board_results
    
    except Exception as e:
        print(f"ERROR fetching pair summary: {e}")
        return None

def main():
    print(f"\n{'='*70}")
    print(f"Fetching missing pair data from vugraph (pairsummary page)")
    print(f"Pair #11: HACI KANTARCI - YAŞAR KARATOPRAK (EW)")
    print(f"Event: {EVENT_ID}")
    print(f"{'='*70}\n")
    
    # Load current board_results.json
    try:
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"ERROR: Failed to load {OUTPUT_FILE}: {e}")
        return False
    
    if 'boards' not in data:
        print(f"ERROR: Invalid {OUTPUT_FILE} structure")
        return False
    
    # Fetch pair summary
    print("Fetching pair summary from vugraph...\n")
    board_results = fetch_pair_summary()
    
    if not board_results:
        print("\nERROR: Failed to fetch pair summary")
        return False
    
    print(f"\nFound {len(board_results)} boards in pair summary")
    
    # Update board_results.json
    updated_count = 0
    
    for board_num, result in board_results.items():
        board_key = f'405376_{board_num}'
        
        if board_key not in data['boards']:
            print(f"\nBoard {board_num}: Board not in database, skipping")
            continue
        
        board_data = data['boards'][board_key]
        results = board_data.get('results', [])
        
        # Check if HACI KANTARCI already exists
        pair_exists = False
        for i, r in enumerate(results):
            if 'HACI' in r.get('pair_names', ''):
                pair_exists = True
                print(f"Board {board_num}: HACI KANTARCI already exists, updating...")
                results[i] = result
                updated_count += 1
                break
        
        if not pair_exists:
            print(f"Board {board_num}: Adding HACI KANTARCI to results")
            results.append(result)
            updated_count += 1
        
        board_data['results'] = results
        data['boards'][board_key] = board_data
    
    # Save updated data
    if updated_count > 0:
        try:
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"\n{'='*70}")
            print(f"SUCCESS: Updated {updated_count} boards with HACI KANTARCI data")
            print(f"File saved: {OUTPUT_FILE}")
            print(f"{'='*70}\n")
            return True
        except Exception as e:
            print(f"\nERROR: Failed to save {OUTPUT_FILE}: {e}")
            return False
    else:
        print(f"\nNo updates made")
        return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
