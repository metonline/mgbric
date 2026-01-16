#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced scraper that follows the user workflow:
1. Event results page → Extract pair links
2. Pair detail page → Extract board links they played
3. Board detail page → Extract score for that board
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import sys
import io
import re
from urllib.parse import urljoin, urlparse, parse_qs

# Set stdout encoding to UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

EVENT_ID = "404377"
SECTION = "A"
BASE_URL = "https://clubs.vugraph.com/hosgoru/"
DB_FILE = "hands_database.json"

def get_event_results_page():
    """Fetch the main event results page"""
    url = f"{BASE_URL}eventresults.php?event={EVENT_ID}"
    
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        return response.content
    except Exception as e:
        print(f"Error fetching event results: {e}")
        return None

def extract_pair_links(html_content):
    """Extract pair names and their detail page links"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    pairs = {'N-S': [], 'E-W': []}
    
    # Find all links that might be pair detail pages
    all_links = soup.find_all('a')
    
    for link in all_links:
        href = link.get('href', '')
        link_text = link.get_text(strip=True)
        
        # Look for pairdetail.php links
        if 'pairdetail.php' in href or 'pairresults.php' in href:
            # Extract direction from URL or context
            if 'direction=NS' in href or 'direction=N-S' in href:
                pair_data = {
                    'name': link_text,
                    'url': urljoin(BASE_URL, href)
                }
                if pair_data not in pairs['N-S']:
                    pairs['N-S'].append(pair_data)
            elif 'direction=EW' in href or 'direction=E-W' in href:
                pair_data = {
                    'name': link_text,
                    'url': urljoin(BASE_URL, href)
                }
                if pair_data not in pairs['E-W']:
                    pairs['E-W'].append(pair_data)
    
    # If no links found by direction, try to infer from position
    if not pairs['N-S'] and not pairs['E-W']:
        # Look for all pairdetail links and try to match with visible text
        tables = soup.find_all('table')
        current_direction = None
        
        for table in tables:
            header_text = table.get_text()
            if 'Kuzey' in header_text or 'Güney' in header_text:
                current_direction = 'N-S'
            elif 'Doğu' in header_text or 'Batı' in header_text:
                current_direction = 'E-W'
            
            # Find links in this table
            table_links = table.find_all('a')
            for link in table_links:
                href = link.get('href', '')
                link_text = link.get_text(strip=True)
                
                if 'pairdetail' in href or 'pairresults' in href:
                    pair_data = {
                        'name': link_text,
                        'url': urljoin(BASE_URL, href)
                    }
                    if current_direction and pair_data not in pairs[current_direction]:
                        pairs[current_direction].append(pair_data)
    
    return pairs

def fetch_pair_page(pair_url):
    """Fetch individual pair's detail page"""
    try:
        response = requests.get(pair_url, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            return response.content
        else:
            print(f"        HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"        Error: {e}")
        return None

def extract_board_links_from_pair_page(html_content):
    """Extract board links from pair's detail page"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    board_links = {}
    
    # Find all table rows that might contain board data
    tables = soup.find_all('table')
    
    for table in tables:
        rows = table.find_all('tr')
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                board_text = cells[0].get_text(strip=True)
                
                # Check if first cell contains board number
                if board_text.isdigit():
                    board_num = int(board_text)
                    
                    # Look for link in this row
                    link = row.find('a')
                    if link:
                        href = link.get('href', '')
                        if href:
                            board_links[board_num] = urljoin(BASE_URL, href)
    
    return board_links

def fetch_board_score(board_url):
    """Fetch and extract score from board detail page"""
    try:
        response = requests.get(board_url, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for board information and score
        # Usually in a table or display area showing contract and score
        
        # Try to find text with "Contract" or "Score"
        text_content = soup.get_text()
        
        # Extract contract - look for pattern like "4S", "3NT", etc.
        contract_match = re.search(r'(7|6|5|4|3|2|1)\s*([♠♥♦♣SDHC]|[A-Z])\s*', text_content)
        contract = contract_match.group(0).strip() if contract_match else '-'
        
        # Extract score percentage
        score_match = re.search(r'(\d+(?:\.\d+)?)\s*%', text_content)
        score = float(score_match.group(1)) if score_match else 0
        
        # Extract result (down/up/equal - shows as negative/positive/0)
        result_match = re.search(r'([+-]\d+|=)', text_content)
        result = result_match.group(0) if result_match else '-'
        
        return {
            'contract': contract,
            'result': result,
            'score': score
        }
    
    except Exception as e:
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
        return True
    except Exception as e:
        print(f"Error saving database: {e}")
        return False

def main():
    print("=" * 70)
    print("Advanced Board Results Scraper")
    print("=" * 70)
    
    print("\nStep 1: Fetching event results page...")
    event_html = get_event_results_page()
    if not event_html:
        return
    
    print("Step 2: Extracting pair links...")
    pairs = extract_pair_links(event_html)
    
    ns_count = len(pairs['N-S'])
    ew_count = len(pairs['E-W'])
    print(f"  Found {ns_count} N-S pairs and {ew_count} E-W pairs\n")
    
    if ns_count == 0 and ew_count == 0:
        print("❌ No pair links found. HTML structure may be different.")
        print("Please check the Vugraph page structure and adjust the scraper.")
        return
    
    # Load database
    db = load_database()
    if not db:
        return
    
    event_key = "hosgoru_04_01_2026"
    if event_key not in db["events"]:
        print(f"Event {event_key} not found")
        return
    
    board_data = db["events"][event_key]["boards"]["1"]
    board_data["results"] = []
    
    # Process N-S pairs
    print("Step 3: Fetching N-S pair board results...")
    for i, pair in enumerate(pairs['N-S'], 1):
        print(f"\n  [{i}/{ns_count}] {pair['name']}")
        pair_html = fetch_pair_page(pair['url'])
        
        if pair_html:
            board_links = extract_board_links_from_pair_page(pair_html)
            
            if 1 in board_links:
                print(f"        Found Board 1 link, fetching score...")
                board_score = fetch_board_score(board_links[1])
                
                if board_score:
                    result_entry = {
                        "pair_names": pair['name'],
                        "pair_num": str(i),
                        "direction": "N-S",
                        "contract": board_score['contract'],
                        "result": board_score['result'],
                        "score": board_score['score']
                    }
                    board_data["results"].append(result_entry)
                    print(f"        ✓ {board_score['contract']} {board_score['result']} - {board_score['score']}%")
                else:
                    print(f"        ✗ Could not extract score")
            else:
                print(f"        - Board 1 not played by this pair")
        
        time.sleep(0.5)
    
    # Process E-W pairs
    print(f"\n\nStep 4: Fetching E-W pair board results...")
    for i, pair in enumerate(pairs['E-W'], 1):
        print(f"\n  [{i}/{ew_count}] {pair['name']}")
        pair_html = fetch_pair_page(pair['url'])
        
        if pair_html:
            board_links = extract_board_links_from_pair_page(pair_html)
            
            if 1 in board_links:
                print(f"        Found Board 1 link, fetching score...")
                board_score = fetch_board_score(board_links[1])
                
                if board_score:
                    result_entry = {
                        "pair_names": pair['name'],
                        "pair_num": str(i),
                        "direction": "E-W",
                        "contract": board_score['contract'],
                        "result": board_score['result'],
                        "score": board_score['score']
                    }
                    board_data["results"].append(result_entry)
                    print(f"        ✓ {board_score['contract']} {board_score['result']} - {board_score['score']}%")
                else:
                    print(f"        ✗ Could not extract score")
            else:
                print(f"        - Board 1 not played by this pair")
        
        time.sleep(0.5)
    
    # Save database
    if save_database(db):
        print(f"\n\n✅ Board 1 updated with {len(board_data['results'])} pair results")
    else:
        print("\n❌ Failed to save database")

if __name__ == "__main__":
    main()
