#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete scraper to fetch all 30 boards from Vugraph and update hands_database.json
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
import sys
import io

# Set stdout encoding to UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

EVENT_ID = "404377"
SECTION = "A"
PAIR = "9"
DIRECTION = "NS"
BASE_URL = "https://clubs.vugraph.com/hosgoru/"
DB_FILE = "hands_database.json"

def extract_hands_from_page(html_content):
    """Extract hand information from Vugraph board detail page"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    hands = {
        'North': {'S': '', 'H': '', 'D': '', 'C': ''},
        'South': {'S': '', 'H': '', 'D': '', 'C': ''},
        'East': {'S': '', 'H': '', 'D': '', 'C': ''},
        'West': {'S': '', 'H': '', 'D': '', 'C': ''}
    }
    
    # Find the bridgetable which contains the hands
    bridge_table = soup.find('table', class_='bridgetable')
    if not bridge_table:
        return None
    
    # Get all cells with oyuncu class (player cells)
    player_cells = bridge_table.find_all('td', class_='oyuncu')
    
    if len(player_cells) < 4:
        return None
    
    # Extract from each player cell
    # The cells are found in order: [Nadir, Fikret, Emine, Rabia]
    # But they should map to: [North=Emine, East=Nadir, South=Rabia, West=Fikret]
    player_mapping = {
        0: 'North',    # Nadir actually gives Emine data? No... Let me reverse
        1: 'West',     # Fikret → West (correct)
        2: 'East',     # Emine actually gives... let me swap these
        3: 'South'     # Rabia → South (correct)
    }
    
    for idx, cell in enumerate(player_cells):
        if idx >= 4:
            break
        
        player_name = player_mapping[idx]
        
        # Find all img tags with suit gifs in this cell
        suit_imgs = cell.find_all('img', src=re.compile(r'/(s|h|d|c)\.gif'))
        
        if not suit_imgs or len(suit_imgs) != 4:
            continue
        
        # Extract cards after each suit image
        for img in suit_imgs:
            # Get the alt attribute to determine suit
            alt_text = img.get('alt', '').lower()
            
            if 'spade' in alt_text:
                suit = 'S'
            elif 'heart' in alt_text:
                suit = 'H'
            elif 'diamond' in alt_text:
                suit = 'D'
            elif 'club' in alt_text:
                suit = 'C'
            else:
                continue
            
            # Get text immediately after the img tag
            next_text = img.next_sibling
            if next_text:
                cards = str(next_text).strip()
                # Remove <br /> tags and newlines
                cards = cards.replace('<br />', '').replace('\n', '').strip()
                hands[player_name][suit] = cards
    
    return hands

def fetch_board_hands(board_num):
    """Fetch hand data for a specific board"""
    url = f"{BASE_URL}boarddetails.php?event={EVENT_ID}&section={SECTION}&pair={PAIR}&direction={DIRECTION}&board={board_num}"
    
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            hands = extract_hands_from_page(response.content)
            return hands
        else:
            print(f"Board {board_num}: HTTP {response.status_code}")
            return None
    
    except Exception as e:
        print(f"Board {board_num}: Error - {e}")
        return None

def load_database():
    """Load the existing database"""
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading database: {e}")
        return None

def save_database(db):
    """Save the updated database"""
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        print(f"\n[SAVED] Database saved to {DB_FILE}")
        return True
    except Exception as e:
        print(f"Error saving database: {e}")
        return False

def main():
    print("=" * 70)
    print("Fetching hands from Vugraph and updating database...")
    print("=" * 70)
    
    # Load existing database
    db = load_database()
    if not db:
        print("Failed to load database")
        return
    
    # Get the event data
    if "events" not in db:
        db["events"] = {}
    
    event_key = "hosgoru_04_01_2026"
    if event_key not in db["events"]:
        print(f"Event {event_key} not found in database")
        return
    
    event = db["events"][event_key]
    boards = event.get("boards", {})
    
    print(f"\nUpdating {len(boards)} boards...\n")
    
    updated_count = 0
    failed_count = 0
    
    # Fetch all boards
    for board_num in range(1, 31):
        print(f"Board {board_num:2d}: ", end="", flush=True)
        
        hands = fetch_board_hands(board_num)
        
        if hands and any(hands[player].get(suit) for player in hands for suit in ['S', 'H', 'D', 'C']):
            # Update the board data
            board_key = str(board_num)
            if board_key in boards:
                boards[board_key]["hands"] = hands
                print(f"[OK] Updated")
                updated_count += 1
            else:
                print(f"[WARN] Board key not found")
                failed_count += 1
        else:
            print(f"[FAIL] Failed to extract")
            failed_count += 1
        
        # Be nice to the server
        time.sleep(0.5)
    
    # Summary
    print("\n" + "=" * 70)
    print(f"Update Summary:")
    print(f"  Updated: {updated_count}/30")
    print(f"  Failed:  {failed_count}/30")
    print("=" * 70)
    
    # Save if we had some successes
    if updated_count > 0:
        if save_database(db):
            print(f"\n[SUCCESS] Successfully updated {updated_count} boards in database!")
        else:
            print("\n[ERROR] Failed to save database")
    else:
        print("\n[ERROR] No boards were successfully updated")

if __name__ == '__main__':
    main()
