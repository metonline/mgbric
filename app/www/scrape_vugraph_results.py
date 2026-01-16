#!/usr/bin/env python3
"""
Scraper for Vugraph tournament results
Fetches all board results and pair information for event 404377 (Hoşgörü tournament)
"""

import requests
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

# Base URL for Vugraph
BASE_URL = "https://clubs.vugraph.com/hosgoru/"
EVENT_ID = "404377"
SECTION = "A"

def fetch_pairs_list():
    """Fetch list of all pairs in the tournament"""
    url = f"{BASE_URL}pairsummary.php?event={EVENT_ID}&section={SECTION}"
    
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')
        
        pairs = []
        # Look for pair links in the page
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'pair=' in href:
                # Extract pair number from URL
                match = re.search(r'pair=(\d+)', href)
                if match:
                    pair_num = match.group(1)
                    pair_name = link.text.strip()
                    if pair_name and pair_num not in [p[0] for p in pairs]:
                        pairs.append((pair_num, pair_name))
        
        print(f"Found {len(pairs)} pairs")
        return pairs
    except Exception as e:
        print(f"Error fetching pairs list: {e}")
        return []

def fetch_board_results(pair, direction, board):
    """Fetch results for a specific board and pair"""
    url = f"{BASE_URL}boarddetails.php?event={EVENT_ID}&section={SECTION}&pair={pair}&direction={direction}&board={board}"
    
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')
        
        results = []
        
        # Find the main results table
        tables = soup.find_all('table')
        
        # Look for table with contract results (Kontrat, Dekleran, Sonuç, Atak, Skor, %)
        for table in tables:
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 6:
                    # Try to parse: Contract | Declarer | Result | Attack | Score | %
                    contract_text = cells[0].text.strip()
                    declarer = cells[1].text.strip()
                    result = cells[2].text.strip()
                    attack = cells[3].text.strip()
                    score_text = cells[4].text.strip()
                    percent_text = cells[5].text.strip()
                    
                    # Check if this looks like a valid result row
                    if contract_text and declarer and percent_text and '%' in percent_text:
                        try:
                            score_percent = float(percent_text.replace('%', '').strip())
                            results.append({
                                'contract': contract_text,
                                'declarer': declarer,
                                'result': result,
                                'attack': attack,
                                'score': score_percent
                            })
                        except ValueError:
                            pass
        
        return results
    except Exception as e:
        print(f"Error fetching board {board} for pair {pair}: {e}")
        return []

def get_pair_names_from_summary(pair):
    """Get pair names from summary page"""
    url = f"{BASE_URL}pairsummary.php?event={EVENT_ID}&section={SECTION}&pair={pair}&direction=NS"
    
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for pair name in page title or header
        title = soup.find('h3') or soup.find('h2')
        if title:
            text = title.text.strip()
            # Extract pair names - usually in format "NAME1 - NAME2"
            if ' - ' in text:
                parts = text.split(' - ')
                for part in parts:
                    if len(part) > 3:
                        return part.strip()
        
        return f"Pair {pair}"
    except Exception as e:
        return f"Pair {pair}"

def main():
    print("Starting Vugraph results scraper for event", EVENT_ID)
    
    # Load existing database
    try:
        with open('hands_database.json', 'r', encoding='utf-8') as f:
            database = json.load(f)
    except:
        print("Could not load hands_database.json")
        return
    
    # Get event
    event = database.get('events', {}).get('hosgoru_04_01_2026', {})
    boards = event.get('boards', {})
    
    print(f"Found {len(boards)} boards in database")
    
    # Fetch pairs list
    print("Fetching pairs list...")
    pairs = fetch_pairs_list()
    
    if not pairs:
        print("No pairs found. Using default pair numbers 1-20...")
        pairs = [(str(i), f"Pair {i}") for i in range(1, 21)]
    
    # For each board, fetch all results
    boards_updated = 0
    for board_key in sorted(boards.keys(), key=lambda x: int(x)):
        board_num = int(board_key)
        print(f"\nFetching results for Board {board_num}...")
        
        all_results = []
        
        # Fetch results for all pairs
        for pair, pair_name in pairs:
            # Try both directions
            for direction in ['NS', 'EW']:
                print(f"  Fetching pair {pair} ({direction})...", end='', flush=True)
                
                results = fetch_board_results(pair, direction, board_num)
                
                if results:
                    print(f" found {len(results)} results")
                    for result in results:
                        all_results.append({
                            'pair_names': pair_name,
                            'pair_num': pair,
                            'direction': direction,
                            'contract': result['contract'],
                            'declarer': result['declarer'],
                            'result': result['result'],
                            'score': result['score']
                        })
                else:
                    print(" no results")
                
                # Be nice to the server
                time.sleep(0.5)
        
        # Sort by score descending
        all_results.sort(key=lambda x: x['score'], reverse=True)
        
        # Update board with results
        if all_results:
            boards[board_key]['results'] = all_results
            boards_updated += 1
            print(f"  Board {board_num}: Added {len(all_results)} results")
    
    # Save updated database
    print(f"\nUpdating database with results from {boards_updated} boards...")
    with open('hands_database.json', 'w', encoding='utf-8') as f:
        json.dump(database, f, ensure_ascii=False, indent=2)
    
    print("Done!")

if __name__ == '__main__':
    main()
