#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart scraper to fetch Board results from individual pair result pages
Extracts pair info from event results page, then fetches each pair's board details
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import sys
import io
import re

# Set stdout encoding to UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

EVENT_ID = "404377"
SECTION = "A"
BASE_URL = "https://clubs.vugraph.com/hosgoru/"
DB_FILE = "hands_database.json"

def get_event_pairs_with_links():
    """Fetch the event results page and extract pair names with their result page links"""
    url = f"{BASE_URL}eventresults.php?event={EVENT_ID}"
    
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')
        
        ns_pairs = []
        ew_pairs = []
        
        # Find all tables
        tables = soup.find_all('table')
        current_direction = None
        
        for table in tables:
            # Check table headers to identify direction
            headers = table.find_all('th')
            header_text = ' '.join([h.get_text(strip=True) for h in headers])
            
            if 'Kuzey' in header_text or 'N-S' in header_text:
                current_direction = 'N-S'
            elif 'Doğu' in header_text or 'E-W' in header_text:
                current_direction = 'E-W'
            
            # Extract rows
            rows = table.find_all('tr')[1:]  # Skip header
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 3:
                    # First cell is rank, second is pair name, third is score
                    rank_text = cells[0].get_text(strip=True)
                    pair_cell = cells[1]
                    pair_name = pair_cell.get_text(strip=True)
                    score_text = cells[2].get_text(strip=True) if len(cells) > 2 else '0'
                    
                    # Try to find link in pair cell
                    link = pair_cell.find('a')
                    pair_url = None
                    if link:
                        pair_url = link.get('href')
                        if pair_url and not pair_url.startswith('http'):
                            pair_url = BASE_URL + pair_url
                    
                    if rank_text.isdigit():
                        pair_info = {
                            'rank': int(rank_text),
                            'name': pair_name,
                            'score': score_text,
                            'url': pair_url
                        }
                        
                        if current_direction == 'N-S':
                            ns_pairs.append(pair_info)
                        elif current_direction == 'E-W':
                            ew_pairs.append(pair_info)
        
        return ns_pairs, ew_pairs
    
    except Exception as e:
        print(f"Error fetching event page: {e}")
        return [], []

def extract_board_results_from_pair_page(html_content):
    """Extract board results from individual pair result page"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Look for board results in tables
    tables = soup.find_all('table')
    
    for table in tables:
        rows = table.find_all('tr')
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 4:
                board_text = cells[0].get_text(strip=True)
                
                # Check if first cell is a board number
                if board_text.isdigit():
                    board_num = int(board_text)
                    
                    if board_num == 1:
                        # Found board 1!
                        contract = cells[1].get_text(strip=True) if len(cells) > 1 else '-'
                        result = cells[2].get_text(strip=True) if len(cells) > 2 else '-'
                        score = cells[3].get_text(strip=True) if len(cells) > 3 else '0'
                        
                        # Clean up score
                        score = score.replace('%', '').strip()
                        try:
                            score = float(score)
                        except:
                            score = 0
                        
                        return {
                            'contract': contract,
                            'result': result,
                            'score': score
                        }
    
    return None

def fetch_pair_board_results(pair_url):
    """Fetch and parse individual pair result page"""
    try:
        response = requests.get(pair_url, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            return extract_board_results_from_pair_page(response.content)
        else:
            print(f"    HTTP {response.status_code}")
            return None
    
    except Exception as e:
        print(f"    Error: {e}")
        return None

def load_database():
    """Load existing database"""
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading database: {e}")
        return None

def save_database(db):
    """Save updated database"""
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        print(f"\n[SAVED] Database updated")
        return True
    except Exception as e:
        print(f"Error saving database: {e}")
        return False

def main():
    print("=" * 70)
    print("Fetching pair information from event results page...")
    print("=" * 70)
    
    # Get all pairs and their URLs
    ns_pairs, ew_pairs = get_event_pairs_with_links()
    
    print(f"\nFound {len(ns_pairs)} N-S pairs and {len(ew_pairs)} E-W pairs\n")
    
    # Load database
    db = load_database()
    if not db:
        print("Failed to load database")
        return
    
    event_key = "hosgoru_04_01_2026"
    if event_key not in db["events"]:
        print(f"Event {event_key} not found")
        return
    
    board_data = db["events"][event_key]["boards"]["1"]
    board_data["results"] = []
    
    # Fetch N-S pairs
    print("Fetching N-S pair results...")
    for pair in ns_pairs:
        pair_name = pair['name']
        pair_url = pair['url']
        
        if pair_url:
            print(f"  {pair['rank']}. {pair_name}...", end=' ')
            result_data = fetch_pair_board_results(pair_url)
            
            if result_data:
                result_entry = {
                    "pair_names": pair_name,
                    "pair_num": str(pair['rank']),
                    "direction": "N-S",
                    "contract": result_data['contract'],
                    "result": result_data['result'],
                    "score": result_data['score']
                }
                board_data["results"].append(result_entry)
                print(f"✓ {result_data['contract']} {result_data['result']} - {result_data['score']}%")
            else:
                print("✗ No board 1 data")
        else:
            print(f"  {pair['rank']}. {pair_name}: No URL found")
        
        time.sleep(0.3)
    
    # Fetch E-W pairs
    print("\nFetching E-W pair results...")
    for pair in ew_pairs:
        pair_name = pair['name']
        pair_url = pair['url']
        
        if pair_url:
            print(f"  {pair['rank']}. {pair_name}...", end=' ')
            result_data = fetch_pair_board_results(pair_url)
            
            if result_data:
                result_entry = {
                    "pair_names": pair_name,
                    "pair_num": str(pair['rank']),
                    "direction": "E-W",
                    "contract": result_data['contract'],
                    "result": result_data['result'],
                    "score": result_data['score']
                }
                board_data["results"].append(result_entry)
                print(f"✓ {result_data['contract']} {result_data['result']} - {result_data['score']}%")
            else:
                print("✗ No board 1 data")
        else:
            print(f"  {pair['rank']}. {pair_name}: No URL found")
        
        time.sleep(0.3)
    
    # Save database
    if save_database(db):
        print(f"\n✅ Board 1 updated with {len(board_data['results'])} pair results")
    else:
        print("\n❌ Failed to save database")

if __name__ == "__main__":
    main()
