#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete data fetching for HACI KANTARCI - YAŞAR KARATOPRAK
Fetch contract and result details from board details pages
"""

import json
import requests
from bs4 import BeautifulSoup
import re
import time

EVENT_ID = '405376'
PAIR_NUM = 11
DIRECTION = 'EW'
SECTION = 'A'
OUTPUT_FILE = 'board_results.json'
REQUEST_TIMEOUT = 15

def fetch_board_details(board_num):
    """Fetch board details page for the pair to get contract info"""
    try:
        # EW direction works in pairsummary, but for board details we use EW directly
        url = f'https://clubs.vugraph.com/hosgoru/boarddetails.php?event={EVENT_ID}&section={SECTION}&pair={PAIR_NUM}&direction={DIRECTION}&board={board_num}'
        
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.encoding = 'iso-8859-9'
        
        if 'Page not Found' in resp.text or 'Sayfa Bulunamadı' in resp.text:
            return None
        
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # Get pair name from h3
        pair_names = ""
        h3 = soup.find('h3')
        if h3:
            h3_text = h3.get_text(strip=True)
            # Format: "20-01-2026 14:00 ... HACI KANTARCI - YAŞAR KARATOPRAK ... Bord 1"
            match = re.search(r'\.\.\.\s*(.+?)\s*\.\.\.\s*Bord', h3_text)
            if match:
                pair_names = match.group(1).strip()
        
        if not pair_names:
            return None
        
        # Find results table
        results_table = soup.find('table', class_='results')
        if not results_table:
            return None
        
        rows = results_table.find_all('tr')
        if not rows:
            return None
        
        # Determine format (IMP vs MP)
        first_row_cells = rows[0].find_all('td')
        first_header = first_row_cells[0].get_text(strip=True) if first_row_cells else ''
        
        # Look for highlighted row
        for row in rows:
            cells = row.find_all('td')
            if len(cells) < 5:
                continue
            
            cell_class = cells[0].get('class', [''])[0] if cells[0].get('class') else ''
            if cell_class not in ['fantastic', 'resultspecial', 'resultsimportant']:
                continue
            
            # Found highlighted row - parse it
            contract = cells[0].get_text(strip=True) if len(cells) > 0 else '-'
            
            # Clean contract text
            for suit in ['S', 'H', 'D', 'C']:
                contract = contract.replace(suit, '♠♥♦♣'[['S', 'H', 'D', 'C'].index(suit)])
            
            declarer = cells[1].get_text(strip=True) if len(cells) > 1 else '-'
            result = cells[2].get_text(strip=True) if len(cells) > 2 else '-'
            
            lead = ''
            score = ''
            percent = 0
            
            if len(cells) >= 8:
                # Format with lead
                lead = cells[3].get_text(strip=True)
                score = cells[4].get_text(strip=True)  # For EW
                percent_text = cells[7].get_text(strip=True) if len(cells) > 7 else '0'
            elif len(cells) >= 7:
                # Format without lead
                score = cells[3].get_text(strip=True)  # For EW
                percent_text = cells[6].get_text(strip=True) if len(cells) > 6 else '0'
                lead = '-'
            
            try:
                percent = float(percent_text.replace(',', '.')) if percent_text else 0
            except:
                percent = 0
            
            return {
                'pair_names': pair_names,
                'direction': DIRECTION,
                'contract': contract,
                'declarer': declarer,
                'result': result,
                'lead': lead,
                'score': score,
                'percent': percent
            }
        
        return None
    
    except Exception as e:
        return None

def main():
    print(f"\n{'='*70}")
    print(f"Fetching board details for HACI KANTARCI - YAŞAR KARATOPRAK")
    print(f"Event: {EVENT_ID}, Pair: {PAIR_NUM} (EW)")
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
    
    # Fetch and update all boards
    updated_count = 0
    
    # Priority boards based on what we know from pairsummary: 1-21, 25-27
    boards_to_fetch = list(range(1, 22)) + list(range(25, 28))
    
    for board_num in boards_to_fetch:
        board_key = f'405376_{board_num}'
        
        if board_key not in data['boards']:
            continue
        
        board_data = data['boards'][board_key]
        results = board_data.get('results', [])
        
        # Check if needs update
        haci_result = None
        haci_index = -1
        for i, r in enumerate(results):
            if 'HACI' in r.get('pair_names', ''):
                haci_result = r
                haci_index = i
                break
        
        print(f"Board {board_num}: Fetching from board details page...", end=' ')
        detail = fetch_board_details(board_num)
        time.sleep(0.3)  # Rate limiting
        
        if detail:
            if haci_index >= 0:
                # Update existing
                results[haci_index] = detail
                print(f"UPDATED: {detail['contract']}, {detail['result']}, {detail['score']}")
            else:
                # Add new
                results.append(detail)
                print(f"ADDED: {detail['contract']}, {detail['result']}, {detail['score']}")
            
            updated_count += 1
            board_data['results'] = results
            data['boards'][board_key] = board_data
        else:
            if haci_index >= 0:
                print(f"SKIP (already has data)")
            else:
                print(f"FAIL (no data found)")
    
    # Save
    if updated_count > 0:
        try:
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"\n{'='*70}")
            print(f"SUCCESS: Updated {updated_count} boards with complete data")
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
