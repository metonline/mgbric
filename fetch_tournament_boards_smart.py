#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import json
import re
import os
from datetime import datetime

# Tournament events to fetch (01.01.2026 - 06.01.2026)
EVENTS = [
    (404562, '2026-01-07'),
]

def get_board_details(event_id, board_num, section='A'):
    try:
        # Try both sections and directions for boarddetails
        for section in ['A', 'B']:
            for direction in ['NS', 'EW']:
                for pair in range(1, 31):
                    url = f"https://clubs.vugraph.com/hosgoru/boarddetails.php?event={event_id}&section={section}&pair={pair}&direction={direction}&board={board_num}"
                    response = requests.get(url, timeout=10)
                    response.encoding = 'utf-8'
                    soup = BeautifulSoup(response.content, 'html.parser')
                    text = soup.get_text()
                    # Find all player hand lines
                    hand_lines = re.findall(r'([A-ZÇĞİÖŞÜa-zçğıöşü\s]+) spades ([AKQJT0-9]+) hearts ([AKQJT0-9]+) diamonds ([AKQJT0-9]+) clubs ([AKQJT0-9]+)', text)
                    if len(hand_lines) >= 4:
                        hands = {}
                        for idx, (name, spades, hearts, diamonds, clubs) in enumerate(hand_lines[:4]):
                            seat = ['N', 'E', 'S', 'W'][idx]
                            hands[seat] = {'S': spades, 'H': hearts, 'D': diamonds, 'C': clubs}
                        return hands
        return None
    except Exception as e:
        print(f"      ⚠️  Error fetching board {board_num}: {e}")
        return None
import os
from datetime import datetime

# Tournament events to fetch (01.01.2026 - 06.01.2026)
EVENTS = [
    (404562, '2026-01-07'),
]

def get_tournament_name(event_id):
    """Fetch tournament name from event page"""
    try:
        url = f"https://clubs.vugraph.com/hosgoru/eventresults.php?event={event_id}"
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to extract tournament name
        title = soup.title
        if title:
            text = title.get_text().strip()
            # Usually format: "Club Name | Tournament Name | Date"
            parts = text.split('|')
            if len(parts) > 1:
                return parts[-1].strip() if parts[-1].strip() else f'Tournament {event_id}'
        
        return f'Tournament {event_id}'
    except:
        return f'Tournament {event_id}'

def get_all_pairs(event_id):
    """Get list of all pairs in the tournament"""
    print(f"   📋 Fetching pair list...")
    
    try:
        url = f"https://clubs.vugraph.com/hosgoru/eventresults.php?event={event_id}"
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')
        
        pairs = []
        
        # Method 1: Look for links to pair results
        # Pattern: pairsummary.php?event=XXXX&section=X&pair=X&direction=NS/EW
        pair_links = soup.find_all('a', href=re.compile(r'pairsummary\.php.*pair=\d+'))
        
        seen_pairs = set()
        for link in pair_links:
            href = link.get('href', '')
            pair_match = re.search(r'pair=(\d+)', href)
            section_match = re.search(r'section=([A-Z]+)', href)
            
            if pair_match:
                pair_num = pair_match.group(1)
                section = section_match.group(1) if section_match else 'A'
                key = (pair_num, section)
                
                if key not in seen_pairs:
                    seen_pairs.add(key)
                    pairs.append({'pair': pair_num, 'section': section})
        
        # Method 2: If no pairs found, try to find table rows with pair data
        if not pairs:
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        # First cell might be pair number (Sıra/Order)
                        pair_num_text = cells[0].get_text().strip()
                        
                        # Check if first cell is a number
                        if pair_num_text.isdigit():
                            pair_num = pair_num_text
                            section = 'A'  # Default section
                            key = (pair_num, section)
                            
                            if key not in seen_pairs:
                                seen_pairs.add(key)
                                pairs.append({'pair': pair_num, 'section': section})
        
        print(f"      Found {len(pairs)} pairs")
        return pairs
    
    except Exception as e:
        print(f"      ⚠️  Error fetching pairs: {e}")
        return []

def get_boards_for_pair(event_id, pair_num, section, direction='NS'):
    """Get board numbers that a specific pair played"""
    try:
        url = f"https://clubs.vugraph.com/hosgoru/pairsummary.php?event={event_id}&section={section}&pair={pair_num}&direction={direction}"
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')
        
        boards = set()
        
        # Look for tables with board data
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) > 0:
                    # First cell should contain board number (Bord)
                    board_text = cells[0].get_text().strip()
                    
                    # Check if it's a number
                    if board_text.isdigit():
                        boards.add(int(board_text))
        
        # Fallback: look for board numbers in text
        if not boards:
            text = soup.get_text()
            # Look for "Bord N" pattern
            board_match = re.findall(r'[Bb]ord\s+(\d+)', text)
            for match in board_match:
                boards.add(int(match))
        
        return boards
    
    except Exception as e:
        return set()

def get_all_board_numbers(event_id):
    """Get all unique board numbers played in the tournament"""
    print(f"   🔍 Collecting all board numbers...")
    
    pairs = get_all_pairs(event_id)
    
    if not pairs:
        print(f"      ⚠️  No pairs found")
        return set()
    
    all_boards = set()
    
    for i, pair_info in enumerate(pairs[:10]):  # Limit to first 10 pairs to save time
        pair_num = pair_info['pair']
        section = pair_info['section']
        
        # Get boards for this pair (NS direction)
        boards = get_boards_for_pair(event_id, pair_num, section, 'NS')
        all_boards.update(boards)
        
        if (i + 1) % 3 == 0:
            print(f"      Scanned {i + 1} pairs, found {len(all_boards)} unique boards...")
    
    print(f"      ✅ Found {len(all_boards)} unique boards: {sorted(all_boards)}")
    return all_boards

def parse_hand_string(hand_str):
    """Parse hand string"""
    if not hand_str or hand_str.strip() == '-':
        return {'S': '', 'H': '', 'D': '', 'C': ''}
    
    result = {'S': '', 'H': '', 'D': '', 'C': ''}
    hand_str = hand_str.strip()
    
    # Try format with suit letters: SAKQ9 HT3 DKT7 CQJ2
    suit_order = ['S', 'H', 'D', 'C']
    parts = hand_str.split()
    
    for i, part in enumerate(parts):
        if i < len(suit_order) and len(part) > 1:
            suit = part[0]
            cards = part[1:]
            if suit in result:
                result[suit] = cards
    
    return result

def fetch_board_details(event_id, board_num):
    """Fetch complete details for a specific board"""
    try:
        url = f"https://clubs.vugraph.com/hosgoru/boardsummary.php?event={event_id}&board={board_num}"
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')
        
        text = soup.get_text()
        
        # Extract dealer and vulnerability
        dealer_match = re.search(r'[Dd]ealer\s*[:\s]+([NEWS])', text)
        dealer = dealer_match.group(1).upper() if dealer_match else 'N'
        
        vuln_match = re.search(r'[Vv]uln[a-z]*\s*[:\s]+([^,\n]+)', text)
        vulnerability = vuln_match.group(1).strip() if vuln_match else '-'
        
        # Try to extract hands
        hands = {
            'N': {'S': '', 'H': '', 'D': '', 'C': ''},
            'S': {'S': '', 'H': '', 'D': '', 'C': ''},
            'E': {'S': '', 'H': '', 'D': '', 'C': ''},
            'W': {'S': '', 'H': '', 'D': '', 'C': ''}
        }
        
        # Look for hand patterns
        for player_name, abbr in [('North', 'N'), ('South', 'S'), ('East', 'E'), ('West', 'W')]:
            pattern = f"{player_name}.*?([SHDCA2-9]+\\s+[SHDCA2-9]+\\s+[SHDCA2-9]+\\s+[SHDCA2-9]+)"
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            
            if match:
                hands[abbr] = parse_hand_string(match.group(1))
        
        has_hands = any(any(hand.values()) for hand in hands.values())
        
        if has_hands:
            return {
                'dealer': dealer,
                'vulnerability': vulnerability,
                'N': hands['N'],
                'S': hands['S'],
                'E': hands['E'],
                'W': hands['W']
            }
        
        return None
    
    except Exception as e:
        print(f"         ⚠️  Error fetching board {board_num}: {e}")
        return None

def fetch_tournament(event_id, tournament_date):
    """Fetch all boards for a tournament"""
    print(f"\n🏆 Event {event_id} ({tournament_date})")
    
    tournament_name = get_tournament_name(event_id)
    print(f"   Name: {tournament_name}")
    
    # Get all unique board numbers
    board_numbers = get_all_board_numbers(event_id)
    
    if not board_numbers:
        print(f"   ❌ No boards found")
        return {}, tournament_name
    
    # Fetch each board
    print(f"   📥 Fetching {len(board_numbers)} boards...")
    
    boards = {}
    for i, board_num in enumerate(sorted(board_numbers), 1):
        board_data = fetch_board_details(event_id, board_num)
        
        if board_data:
            boards[str(board_num)] = board_data
            if i % 5 == 0:
                print(f"      Fetched {i}/{len(board_numbers)}...")
        
        # Rate limiting
        import time
        time.sleep(0.5)
    
    print(f"   ✅ Fetched {len(boards)} boards")
    return boards, tournament_name

def main():
    print("=" * 70)
    print("🎯 Intelligent Tournament Board Fetcher")
    print("=" * 70)
    print("\nStrategy:")
    print("1. Find all pairs in tournament")
    print("2. Get board numbers each pair played")
    print("3. Collect all unique board numbers")
    print("4. Fetch complete details for each unique board")
    print("5. Merge into database\n")
    
    # Load existing database
    db_path = r'C:\Users\metin\Desktop\BRIC\app\www\hands_database.json'
    
    print(f"📂 Loading existing database...")
    if os.path.exists(db_path):
        with open(db_path, 'r', encoding='utf-8') as f:
            all_boards = json.load(f)
        print(f"   Loaded {len(all_boards)} existing boards")
    else:
        all_boards = {}
        print(f"   Creating new database")
    
    board_counter = max([int(k) for k in all_boards.keys() if k.isdigit()]) if all_boards else 0
    
    # Fetch each tournament
    for event_id, tournament_date in EVENTS:
        try:
            boards, tournament_name = fetch_tournament(event_id, tournament_date)
            
            if boards:
                for board_num, board_data in boards.items():
                    board_counter += 1
                    
                    all_boards[str(board_counter)] = {
                        'date': tournament_date,
                        'tournament': tournament_name,
                        'board_num': int(board_num),
                        'dealer': board_data['dealer'],
                        'vulnerability': board_data['vulnerability'],
                        'N': board_data['N'],
                        'S': board_data['S'],
                        'E': board_data['E'],
                        'W': board_data['W']
                    }
        
        except Exception as e:
            print(f"\n   ❌ Error processing event {event_id}: {e}")
    
    # Save database
    print(f"\n{'=' * 70}")
    print("💾 Saving database...")
    
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(all_boards, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Database saved!")
    print(f"   Location: {db_path}")
    print(f"   Total boards: {len(all_boards)}")
    
    # Summary
    boards_by_date = {}
    for board_data in all_boards.values():
        if isinstance(board_data, dict):
            date = board_data.get('date', 'unknown')
            if date not in boards_by_date:
                boards_by_date[date] = 0
            boards_by_date[date] += 1
    
    print(f"\n📊 Boards by Date:")
    for date in sorted(boards_by_date.keys()):
        print(f"   {date}: {boards_by_date[date]} boards")

if __name__ == '__main__':
    main()
