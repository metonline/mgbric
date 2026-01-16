#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch hands from Vugraph and add to existing database
Fetches tournaments from 01.01.2026 onwards and merges with hands_database.json
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timedelta
import os

def parse_hand_string(hand_str):
    """Parse hand string like 'S:AK9 H:QJ8 D:K87 C:AQJ' to dict"""
    if not hand_str or hand_str.strip() == '-':
        return {'S': '-', 'H': '-', 'D': '-', 'C': '-'}
    
    result = {}
    # Handle formats like "SAKQ9HT3DKT7CQJ2" (no separators)
    hand_str = hand_str.strip()
    
    # Try format with colons: S:AK9 H:QJ8 D:K87 C:AQJ
    if ':' in hand_str:
        for suit_part in hand_str.split():
            if ':' in suit_part:
                suit, cards = suit_part.split(':')
                result[suit] = cards
    else:
        # Try continuous format: SAKQ9HT3DKT7CQJ2
        suits = ['S', 'H', 'D', 'C']
        current_suit = 0
        current_cards = ''
        
        for char in hand_str:
            if char in suits:
                if current_cards:
                    result[suits[current_suit]] = current_cards
                    current_cards = ''
                current_suit = suits.index(char)
            else:
                current_cards += char
        
        if current_cards:
            result[suits[current_suit]] = current_cards
    
    return {s: result.get(s, '-') for s in ['S', 'H', 'D', 'C']}

def fetch_board(event_id, board_num):
    """Fetch single board details"""
    url = f"https://clubs.vugraph.com/hosgoru/boardsummary.php?event={event_id}&board={board_num}"
    
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find board info
        board_data = {
            'board_num': board_num,
            'dealer': None,
            'vulnerability': None,
            'hands': {},
            'results': []
        }
        
        # Look for board header/table with dealer and vulnerability
        text = soup.get_text()
        
        # Try to find dealer (N, S, E, W) and vulnerability info
        # This varies by website layout - we'll try common patterns
        dealer_match = re.search(r'[Dd]ealer\s*[:\s]+([NEWS])', text)
        if dealer_match:
            board_data['dealer'] = dealer_match.group(1).upper()
        else:
            # Default to North
            board_data['dealer'] = 'N'
        
        vuln_match = re.search(r'[Vv]uln[a-z]*\s*[:\s]+([^,\n]+)', text)
        if vuln_match:
            vuln_text = vuln_match.group(1).strip()
            if 'none' in vuln_text.lower():
                board_data['vulnerability'] = 'None'
            elif 'both' in vuln_text.lower():
                board_data['vulnerability'] = 'Both'
            elif 'e' in vuln_text.lower() or 'east' in vuln_text.lower():
                board_data['vulnerability'] = 'E'
            elif 'w' in vuln_text.lower() or 'west' in vuln_text.lower():
                board_data['vulnerability'] = 'W'
        else:
            board_data['vulnerability'] = 'None'
        
        # Find hands (N, S, E, W)
        # Look for patterns like "North: SACK9... " or hand display tables
        for player in ['North', 'South', 'East', 'West']:
            pattern = f"{player.lower()}.*?[:\s]+([SHDCATK2-9]+(?:[SHDCA2-9]*)?)"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                hand_str = match.group(1)
                board_data['hands'][player] = parse_hand_string(hand_str)
        
        return board_data
    
    except Exception as e:
        print(f"Error fetching board {board_num}: {e}")
        return None

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch hands from Vugraph and add to existing database
Fetches tournaments from 01.01.2026 onwards and merges with hands_database.json
Structure: {
  "1": { "N": {...}, "E": {...}, "S": {...}, "W": {...} },
  "2": { ... },
  ...
}
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timedelta
import os

def parse_hand_string(hand_str):
    """Parse hand string like 'S:AK9 H:QJ8 D:K87 C:AQJ' to dict"""
    if not hand_str or hand_str.strip() == '-':
        return {'S': '', 'H': '', 'D': '', 'C': ''}
    
    result = {}
    hand_str = hand_str.strip()
    
    # Try format with colons: S:AK9 H:QJ8 D:K87 C:AQJ
    if ':' in hand_str:
        for suit_part in hand_str.split():
            if ':' in suit_part:
                suit, cards = suit_part.split(':')
                result[suit] = cards
    else:
        # Try continuous format: SAKQ9HT3DKT7CQJ2
        suits = ['S', 'H', 'D', 'C']
        current_suit = 0
        current_cards = ''
        
        for char in hand_str:
            if char in suits:
                if current_cards:
                    result[suits[current_suit]] = current_cards
                    current_cards = ''
                current_suit = suits.index(char)
            else:
                current_cards += char
        
        if current_cards:
            result[suits[current_suit]] = current_cards
    
    return {s: result.get(s, '') for s in ['S', 'H', 'D', 'C']}

def fetch_board(event_id, board_num):
    """Fetch single board details from Vugraph"""
    url = f"https://clubs.vugraph.com/hosgoru/boardsummary.php?event={event_id}&board={board_num}"
    
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')
        
        board_data = {
            'board_num': board_num,
            'hands': {'N': {}, 'E': {}, 'S': {}, 'W': {}}
        }
        
        # Find hands (N, S, E, W)
        text = soup.get_text()
        
        for player_abbr, player_name in [('N', 'North'), ('E', 'East'), ('S', 'South'), ('W', 'West')]:
            # Look for "North:" or "N:" patterns followed by hand
            pattern = f"(?:{player_name}|{player_abbr})\\s*:?\\s*(?:[Ss]pades?|[Ss])\\s*([A-Z2-9]+)"
            match = re.search(pattern, text)
            
            if match:
                spades = match.group(1)
                board_data['hands'][player_abbr]['S'] = spades
                
                # Try to get other suits
                pattern_h = f"(?:{player_name}|{player_abbr})\\s*:?.*?(?:[Hh]earts?|[Hh])\\s*([A-Z2-9]*)"
                match_h = re.search(pattern_h, text)
                if match_h:
                    board_data['hands'][player_abbr]['H'] = match_h.group(1)
        
        return board_data if any(board_data['hands'].values()) else None
    
    except Exception as e:
        print(f"    ⚠️  Error fetching board {board_num}: {e}")
        return None

def load_existing_database(db_path):
    """Load existing hands database"""
    if os.path.exists(db_path):
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading existing database: {e}")
    return {}

def save_database(db_path, database):
    """Save hands database to file"""
    try:
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(database, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving database: {e}")
        return False

def main():
    db_path = r'C:\Users\metin\Desktop\BRIC\app\www\hands_database.json'
    
    print("=" * 60)
    print("🌉 Vugraph Tournament Hands Fetcher")
    print("=" * 60)
    
    # Load existing database
    print("\n📂 Loading existing database...")
    existing_db = load_existing_database(db_path)
    
    if not existing_db:
        print("  No existing database found, creating new one")
        existing_db = {}
        highest_board = 0
    else:
        highest_board = max([int(k) for k in existing_db.keys() if k.isdigit()])
        print(f"  ✅ Loaded existing database with {len(existing_db)} boards")
        print(f"     Highest board number: {highest_board}")
    
    print(f"\n🔍 Ready to fetch tournaments from 01.01.2026 onwards")
    print("\n   To add hands, provide tournament IDs (event IDs from Vugraph)")
    print("   Example: fetch_board(404377, 1)")
    print("\n   Vugraph tournaments found on 01.01.2026 - 07.01.2026:")
    print("   - Event 404377: PAZAR SİMULTANE 04-01-2026")
    
    # Prompt for event IDs to fetch
    event_ids_input = input("\n   Enter event IDs to fetch (comma-separated, or press Enter to skip): ").strip()
    
    if not event_ids_input:
        print("\n   No event IDs provided. Exiting...")
        return
    
    try:
        event_ids = [int(e.strip()) for e in event_ids_input.split(',')]
    except ValueError:
        print("❌ Invalid event ID format")
        return
    
    print(f"\n📥 Fetching hands from {len(event_ids)} tournament(s)...")
    total_new_boards = 0
    
    for event_id in event_ids:
        print(f"\n  Tournament Event ID: {event_id}")
        
        boards_found = 0
        consecutive_failures = 0
        
        for board_num in range(1, 101):  # Try up to 100 boards
            board_data = fetch_board(event_id, board_num)
            
            if board_data and any(board_data['hands'].values()):
                highest_board += 1
                board_key = str(highest_board)
                
                existing_db[board_key] = board_data['hands']
                boards_found += 1
                total_new_boards += 1
                consecutive_failures = 0
                print(f"    ✓ Board {board_num} → stored as board {board_key}")
            else:
                consecutive_failures += 1
                if consecutive_failures > 5:
                    # Stop trying if 5 consecutive boards fail
                    break
        
        print(f"    Found {boards_found} boards from event {event_id}")
    
    # Save database
    if total_new_boards > 0:
        print(f"\n💾 Saving database with {total_new_boards} new boards...")
        if save_database(db_path, existing_db):
            total_boards = len(existing_db)
            print(f"✅ Database updated successfully!")
            print(f"   Total boards in database: {total_boards}")
            print(f"   New boards added: {total_new_boards}")
        else:
            print("❌ Failed to save database")
    else:
        print("\n⚠️  No new boards fetched from Vugraph")
        print("   Check event IDs and try again")

if __name__ == '__main__':
    main()
