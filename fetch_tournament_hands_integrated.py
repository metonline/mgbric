#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch hands from Vugraph for all tournaments in database.json
Integrates hands directly into tournament records by extracting event IDs from Links
Structure: Each tournament record gets a "Hands" field with board hands organized by tournament
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
from urllib.parse import urlparse, parse_qs
from collections import defaultdict

def extract_event_id(link):
    """Extract event ID from Vugraph URL"""
    try:
        parsed = urlparse(link)
        params = parse_qs(parsed.query)
        event_id = params.get('event', [None])[0]
        return event_id
    except:
        return None

def parse_hand_string(hand_str):
    """Parse hand string to dict with S, H, D, C keys"""
    if not hand_str or hand_str.strip() in ['-', '']:
        return {'S': '', 'H': '', 'D': '', 'C': ''}
    
    result = {}
    hand_str = hand_str.strip()
    
    # Try format with colons: S:AK9 H:QJ8 D:K87 C:AQJ
    if ':' in hand_str:
        for suit_part in hand_str.split():
            if ':' in suit_part:
                suit, cards = suit_part.split(':')
                result[suit.upper()] = cards
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
    
    # Ensure all suits present
    return {s: result.get(s, '') for s in ['S', 'H', 'D', 'C']}

def fetch_hands_for_event(event_id, num_boards=30):
    """
    Fetch hands for all boards in a tournament event
    Returns: {'1': {'N': {...}, 'E': {...}, 'S': {...}, 'W': {...}}, '2': {...}, ...}
    """
    hands_by_board = {}
    
    print(f"  Fetching hands for event {event_id}...")
    
    for board_num in range(1, num_boards + 1):
        try:
            url = f"https://clubs.vugraph.com/hosgoru/boardsummary.php?event={event_id}&board={board_num}"
            response = requests.get(url, timeout=8)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')
            
            board_text = soup.get_text()
            
            # Extract hands - look for patterns
            hands = {}
            for direction in ['North', 'South', 'East', 'West']:
                # Try multiple patterns
                patterns = [
                    rf"{direction}\s*[:\s]+([AKQJT2-9]*(?:\s+[AKQJT2-9]*)*)",
                    rf"{direction.lower()}.*?[:\s]+([AKQJT2-9]+)",
                ]
                
                hand_found = None
                for pattern in patterns:
                    match = re.search(pattern, board_text, re.IGNORECASE)
                    if match:
                        hand_found = match.group(1)
                        break
                
                if hand_found:
                    hands[direction[0]] = parse_hand_string(hand_found)
                else:
                    hands[direction[0]] = {'S': '', 'H': '', 'D': '', 'C': ''}
            
            # Only add if we found at least some hands
            if any(hands.values()):
                hands_by_board[str(board_num)] = hands
                print(f"    Board {board_num}: OK")
            else:
                print(f"    Board {board_num}: No hands found")
            
            # Rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            print(f"    Board {board_num}: Error - {str(e)[:50]}")
            time.sleep(0.5)
            continue
    
    return hands_by_board if hands_by_board else None

def load_database():
    """Load database.json"""
    try:
        with open('database.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading database: {e}")
        return []

def save_database(data):
    """Save database.json"""
    try:
        with open('database.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Database saved: {len(data)} records")
        return True
    except Exception as e:
        print(f"Error saving database: {e}")
        return False

def parse_date(date_str):
    """Parse Turkish date format DD.MM.YYYY"""
    try:
        from datetime import datetime
        return datetime.strptime(date_str, '%d.%m.%Y')
    except:
        return None

def process_tournaments():
    """
    Main process:
    1. Load database.json
    2. Extract unique tournaments by event ID from 01.01.2026 onwards
    3. Fetch hands for each tournament
    4. Add hands to all records of that tournament
    5. Save updated database
    """
    print("[*] Starting tournament hands fetching (2026 onwards)...\n")
    
    from datetime import datetime
    cutoff_date = datetime.strptime('01.01.2026', '%d.%m.%Y')
    
    # Load database
    database = load_database()
    if not database:
        print("Failed to load database")
        return
    
    print(f"[*] Loaded {len(database)} records")
    
    # Group by tournament (event ID)
    tournaments = defaultdict(list)
    event_info = {}  # Store tournament name and first link for each event
    
    for idx, record in enumerate(database):
        # Filter by date - only 2026 onwards
        date_str = record.get('Tarih', '')
        record_date = parse_date(date_str)
        
        if not record_date or record_date < cutoff_date:
            continue
        
        link = record.get('Link', '')
        event_id = extract_event_id(link)
        
        if event_id:
            tournaments[event_id].append(idx)
            if event_id not in event_info:
                event_info[event_id] = {
                    'name': record.get('Turnuva', 'Unknown'),
                    'link': link,
                    'date': date_str
                }
    
    print(f"[*] Found {len(tournaments)} unique tournaments from 01.01.2026 onwards\n")
    
    # Fetch hands for each tournament
    hands_fetched = 0
    hands_failed = 0
    
    for idx, (event_id, record_indices) in enumerate(sorted(tournaments.items())):
        tournament_name = event_info[event_id]['name']
        tournament_date = event_info[event_id]['date']
        num_records = len(record_indices)
        
        print(f"[{idx+1}/{len(tournaments)}] [EVENT {event_id}] {tournament_date} - {tournament_name} ({num_records} records)")
        
        # Check if hands already exist for this tournament
        if 'Hands' in database[record_indices[0]]:
            print(f"  Hands already fetched - Skipping\n")
            continue
        
        # Fetch hands from Vugraph
        hands = fetch_hands_for_event(event_id, num_boards=30)
        
        if hands:
            # Add hands to all records of this tournament
            for record_idx in record_indices:
                database[record_idx]['Hands'] = hands
                database[record_idx]['HandsFetched'] = True
            
            print(f"  Added {len(hands)} boards to {num_records} records\n")
            hands_fetched += 1
            
            # Save periodically after each tournament
            save_database(database)
        else:
            print(f"  Failed to fetch hands\n")
            hands_failed += 1
        
        # Rate limiting between tournaments
        time.sleep(1)
    
    # Save final database
    print(f"\n[*] Final save of database...")
    save_database(database)
    
    print(f"\n[SUMMARY]")
    print(f"  Total tournaments: {len(tournaments)}")
    print(f"  Successfully fetched: {hands_fetched}")
    print(f"  Failed: {hands_failed}")
    print(f"  Total records updated: {len(database)}")
    print(f"  Database saved to: database.json")

if __name__ == '__main__':
    process_tournaments()
