#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COMPLETE DATA RECOVERY FROM SCRATCH
Fetch ALL pair results for Event 404155, all boards, all pairs from vugraph
This will rebuild board_results.json completely and correctly
"""

import json
import requests
from bs4 import BeautifulSoup
import re
import time

EVENT_ID = '404155'
SECTION = 'A'
OUTPUT_FILE = 'board_results.json'
REQUEST_TIMEOUT = 15

# First, we need to get the list of all pairs and their numbers
def fetch_event_pairs():
    """Get all pairs in the tournament from eventresults page"""
    try:
        url = f'https://clubs.vugraph.com/hosgoru/eventresults.php?event={EVENT_ID}'
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.encoding = 'iso-8859-9'
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        ns_pairs = {}  # {pair_num: "Name1 - Name2"}
        ew_pairs = {}
        
        # Find colored table
        table = soup.find('table', class_='colored')
        if not table:
            return None, None
        
        rows = table.find_all('tr')
        in_ns = False
        in_ew = False
        pair_counter_ns = 0
        pair_counter_ew = 0
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if not cells:
                continue
            
            # Check for section headers (single cell rows with direction text)
            if len(cells) == 1:
                first_cell = cells[0].get_text(strip=True)
                if 'Kuzey' in first_cell or 'North' in first_cell:
                    in_ns = True
                    in_ew = False
                    pair_counter_ns = 0
                    continue
                elif 'Dogu' in first_cell or 'Bati' in first_cell or 'East' in first_cell:
                    in_ew = True
                    in_ns = False
                    pair_counter_ew = 0
                    continue
            
            # Skip header row (Sıra, Çift, Skor)
            if len(cells) >= 2:
                first_text = cells[0].get_text(strip=True)
                if first_text in ['Sira', 'Sıra', 'Rank']:
                    continue
                
                # Parse rank/pair/score rows
                try:
                    rank = int(first_text)
                    pair_name = cells[1].get_text(strip=True)
                    
                    # Get pair number from link if available
                    pair_link = cells[1].find('a', href=True)
                    pair_num = None
                    if pair_link:
                        href = pair_link.get('href', '')
                        match = re.search(r'pair=(\d+)', href)
                        if match:
                            pair_num = int(match.group(1))
                    
                    if pair_num:
                        if in_ns:
                            ns_pairs[pair_num] = pair_name
                        elif in_ew:
                            ew_pairs[pair_num] = pair_name
                
                except (ValueError, IndexError):
                    pass
        
        return ns_pairs if ns_pairs else None, ew_pairs if ew_pairs else None
    
    except Exception as e:
        print(f"ERROR fetching pairs: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def fetch_all_boards_for_pair(pair_num, direction):
    """Fetch all boards for a specific pair using pairsummary"""
    try:
        url = f'https://clubs.vugraph.com/hosgoru/pairsummary.php?event={EVENT_ID}&section={SECTION}&pair={pair_num}&direction={direction}'
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.encoding = 'iso-8859-9'
        
        if 'Page not Found' in resp.text or 'Sayfa Bulunamadı' in resp.text:
            return None
        
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # Get pair names
        pair_names = ""
        h4 = soup.find('h4')
        if h4:
            h4_text = h4.get_text(strip=True)
            pair_names = h4_text.replace('Çift Özeti', '').replace('Cift Ozeti', '').strip()
        
        if not pair_names:
            return None
        
        # Get results table
        tables = soup.find_all('table')
        if len(tables) < 2:
            return None
        
        results_table = tables[1]
        rows = results_table.find_all('tr')
        
        board_results = {}
        
        # Parse rows (skip header)
        for row in rows[1:]:
            cells = row.find_all('td')
            if len(cells) < 4:
                continue
            
            try:
                board_text = cells[0].get_text(strip=True)
                if not board_text.isdigit():
                    continue
                
                board_num = int(board_text)
                opponent = cells[1].get_text(strip=True)
                result = cells[2].get_text(strip=True)
                score = cells[3].get_text(strip=True)
                percent_text = cells[4].get_text(strip=True) if len(cells) > 4 else '0'
                
                try:
                    percent = float(percent_text.replace(',', '.'))
                except:
                    percent = 0
                
                board_results[board_num] = {
                    'pair_names': pair_names,
                    'direction': direction,
                    'contract': opponent,  # Temp - will get from board details
                    'declarer': '-',
                    'result': result,
                    'lead': '-',
                    'score': score,
                    'percent': percent
                }
            
            except Exception as e:
                continue
        
        return board_results if board_results else None
    
    except Exception as e:
        return None

def fetch_board_contract_details(board_num, pair_num, direction):
    """Get contract details from board details page"""
    try:
        url = f'https://clubs.vugraph.com/hosgoru/boarddetails.php?event={EVENT_ID}&section={SECTION}&pair={pair_num}&direction={direction}&board={board_num}'
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.encoding = 'iso-8859-9'
        
        if 'Page not Found' in resp.text or 'Sayfa Bulunamadı' in resp.text:
            return None
        
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # Find results table and get the highlighted row
        results_table = soup.find('table', class_='results')
        if not results_table:
            return None
        
        rows = results_table.find_all('tr')
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) < 5:
                continue
            
            cell_class = cells[0].get('class', [''])[0] if cells[0].get('class') else ''
            if cell_class not in ['fantastic', 'resultspecial', 'resultsimportant']:
                continue
            
            contract = cells[0].get_text(strip=True)
            declarer = cells[1].get_text(strip=True) if len(cells) > 1 else '-'
            
            return {'contract': contract, 'declarer': declarer}
        
        return None
    
    except Exception as e:
        return None

def main():
    print(f"\n{'='*70}")
    print(f"COMPLETE DATA RECOVERY - Event {EVENT_ID}")
    print(f"Fetching ALL pairs for ALL boards from vugraph")
    print(f"{'='*70}\n")
    
    # Step 1: Get all pairs
    print("Step 1: Fetching tournament pair list...")
    ns_pairs, ew_pairs = fetch_event_pairs()
    
    if not ns_pairs or not ew_pairs:
        print("ERROR: Could not fetch pair list")
        return False
    
    print(f"  Found {len(ns_pairs)} NS pairs and {len(ew_pairs)} EW pairs\n")
    
    # Initialize data structure
    data = {
        'boards': {},
        'events': {}
    }
    
    # Initialize all 30 boards
    for board_num in range(1, 31):
        data['boards'][f'{EVENT_ID}_{board_num}'] = {
            'results': []
        }
    
    # Step 2: Fetch all results from pairsummary (for all pairs)
    print("Step 2: Fetching pair summaries...")
    all_pair_results = {}  # {(pair_num, direction): {board_num: result}}
    
    all_pairs = list(ns_pairs.items()) + list(ew_pairs.items())
    
    for i, (pair_num, pair_name) in enumerate(all_pairs):
        direction = 'NS' if pair_num in ns_pairs else 'EW'
        print(f"  [{i+1}/{len(all_pairs)}] Pair #{pair_num} ({direction}): {pair_name[:40]}", end='...')
        
        results = fetch_all_boards_for_pair(pair_num, direction)
        
        if results:
            all_pair_results[(pair_num, direction)] = results
            print(f" OK ({len(results)} boards)")
        else:
            print(f" SKIP")
        
        time.sleep(0.2)
    
    print(f"\n  Total pairs fetched: {len(all_pair_results)}\n")
    
    # Step 3: Get contract details for all boards/pairs
    print("Step 3: Fetching contract details...")
    total_to_fetch = len(all_pair_results) * 30
    count = 0
    
    for (pair_num, direction), board_results in all_pair_results.items():
        for board_num in board_results.keys():
            count += 1
            contract_data = fetch_board_contract_details(board_num, pair_num, direction)
            
            if contract_data:
                board_results[board_num]['contract'] = contract_data['contract']
                board_results[board_num]['declarer'] = contract_data['declarer']
            
            time.sleep(0.1)
            
            if count % 20 == 0:
                print(f"  Processed {count}/{total_to_fetch}...")
    
    # Step 4: Combine results into board structure
    print(f"\nStep 4: Organizing results by board...")
    
    for (pair_num, direction), board_results in all_pair_results.items():
        for board_num, result in board_results.items():
            board_key = f'{EVENT_ID}_{board_num}'
            if board_key in data['boards']:
                data['boards'][board_key]['results'].append(result)
    
    # Step 5: Sort results by percent within each board
    print("Step 5: Sorting results by percentage...")
    
    for board_key in data['boards'].keys():
        results = data['boards'][board_key]['results']
        results.sort(key=lambda x: float(x.get('percent', 0)), reverse=True)
        
        # Add rank
        for rank, result in enumerate(results, 1):
            result['rank'] = rank
        
        data['boards'][board_key]['results'] = results
    
    # Step 6: Save to file
    print(f"\nStep 6: Saving to {OUTPUT_FILE}...")
    
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*70}")
        print(f"SUCCESS: Complete recovery finished!")
        print(f"File saved: {OUTPUT_FILE}")
        
        # Summary
        total_results = sum(len(board['results']) for board in data['boards'].values())
        avg_per_board = total_results // 30 if total_results > 0 else 0
        
        print(f"\nSummary:")
        print(f"  Total boards: 30")
        print(f"  Total pair results: {total_results}")
        print(f"  Average pairs per board: {avg_per_board}")
        print(f"{'='*70}\n")
        
        return True
    
    except Exception as e:
        print(f"ERROR: Failed to save file: {e}")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
