#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch boards from multiple Vugraph events
Uses provided event IDs to fetch complete tournament data
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import os
from datetime import datetime

# Event IDs and their dates
EVENTS = [
    ('404155', '2026-01-01'),  # 01.01.2026
    ('404197', '2026-01-02'),  # 02.01.2026
    ('404275', '2026-01-03'),  # 03.01.2026
    ('404377', '2026-01-04'),  # 04.01.2026
    ('404426', '2026-01-05'),  # 05.01.2026
    ('404498', '2026-01-06'),  # 06.01.2026
]

def get_tournament_name(event_id):
    """Fetch tournament name from event page"""
    try:
        url = f"https://clubs.vugraph.com/hosgoru/eventresults.php?event={event_id}"
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for tournament name in title or headings
        title = soup.title
        if title:
            return title.get_text().strip()
        
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        return f'Tournament {event_id}'
    
    except Exception as e:
        print(f"      Warning: Could not fetch tournament name: {e}")
        return f'Tournament {event_id}'

def parse_hand_string(hand_str):
    """Parse hand string like 'SAKQ9 HT3 DKT7 CQJ2' to dict"""
    if not hand_str or hand_str.strip() == '-':
        return {'S': '-', 'H': '-', 'D': '-', 'C': '-'}
    
    result = {'S': '', 'H': '', 'D': '', 'C': ''}
    hand_str = hand_str.strip()
    
    # Try format with suit letters: SAKQ9 HT3 DKT7 CQJ2
    suit_order = ['S', 'H', 'D', 'C']
    parts = hand_str.split()
    
    for i, part in enumerate(parts):
        if i < len(suit_order) and len(part) > 1:
            # First char is suit, rest is cards
            suit = part[0]
            cards = part[1:]
            if suit in result:
                result[suit] = cards
    
    return result

def fetch_boards_from_event(event_id, tournament_date):
    """Fetch all boards from a specific event"""
    print(f"\n   📥 Event {event_id} ({tournament_date}):")
    
    # Get tournament name
    tournament_name = get_tournament_name(event_id)
    print(f"      Name: {tournament_name}")
    
    boards = {}
    consecutive_failures = 0
    
    for board_num in range(1, 101):  # Try up to 100 boards
        try:
            url = f"https://clubs.vugraph.com/hosgoru/boardsummary.php?event={event_id}&board={board_num}"
            response = requests.get(url, timeout=10)
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text()
            
            # Look for hand patterns (S:AK9 H:QJ8 D:K87 C:AQJ or similar)
            # Extract dealer, vulnerability, and hands
            
            dealer_match = re.search(r'[Dd]ealer\s*[:\s]+([NEWS])', text)
            dealer = dealer_match.group(1).upper() if dealer_match else 'N'
            
            vuln_match = re.search(r'[Vv]uln[a-z]*\s*[:\s]+([^,\n]+)', text)
            vulnerability = vuln_match.group(1).strip() if vuln_match else '-'
            
            # Try to find North, South, East, West hands
            hands = {
                'N': {'S': '', 'H': '', 'D': '', 'C': ''},
                'S': {'S': '', 'H': '', 'D': '', 'C': ''},
                'E': {'S': '', 'H': '', 'D': '', 'C': ''},
                'W': {'S': '', 'H': '', 'D': '', 'C': ''}
            }
            
            # Pattern: North: SAKQ9 HT3 DKT7 CQJ2
            north_pattern = r'[Nn]orth\s*[:\s]*([\w\s]+?)(?:[EeSsWw]ast|$)'
            north_match = re.search(north_pattern, text)
            if north_match:
                hands['N'] = parse_hand_string(north_match.group(1))
            
            south_pattern = r'[Ss]outh\s*[:\s]*([\w\s]+?)(?:[EeWw]est|[Ee]ast|$)'
            south_match = re.search(south_pattern, text)
            if south_match:
                hands['S'] = parse_hand_string(south_match.group(1))
            
            east_pattern = r'[Ee]ast\s*[:\s]*([\w\s]+?)(?:[Ww]est|$)'
            east_match = re.search(east_pattern, text)
            if east_match:
                hands['E'] = parse_hand_string(east_match.group(1))
            
            west_pattern = r'[Ww]est\s*[:\s]*([\w\s]+?)$'
            west_match = re.search(west_pattern, text)
            if west_match:
                hands['W'] = parse_hand_string(west_match.group(1))
            
            # Check if we found any hands
            has_hands = any(
                any(hand.values()) for hand in hands.values()
            )
            
            if has_hands:
                boards[str(board_num)] = {
                    'N': hands['N'],
                    'S': hands['S'],
                    'E': hands['E'],
                    'W': hands['W'],
                    'dealer': dealer,
                    'vulnerability': vulnerability
                }
                
                consecutive_failures = 0
                
                if len(boards) % 10 == 0:
                    print(f"      Fetched {len(boards)} boards...")
            else:
                consecutive_failures += 1
                if consecutive_failures > 15:
                    break
        
        except Exception as e:
            consecutive_failures += 1
            if consecutive_failures > 15:
                break
    
    print(f"      ✅ Fetched {len(boards)} boards")
    return boards, tournament_name

def main():
    print("=" * 70)
    print("🎯 Multi-Event Tournament Data Fetcher")
    print("=" * 70)
    
    print(f"\n📋 Fetching data from {len(EVENTS)} events...")
    
    all_boards = {}
    board_counter = 1
    
    for event_id, tournament_date in EVENTS:
        try:
            boards, tournament_name = fetch_boards_from_event(event_id, tournament_date)
            
            if boards:
                for board_num, board_data in sorted(boards.items(), key=lambda x: int(x[0])):
                    board_key = str(board_counter)
                    
                    all_boards[board_key] = {
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
                    
                    board_counter += 1
        
        except Exception as e:
            print(f"\n   ❌ Error fetching event {event_id}: {e}")
    
    # Save database
    if all_boards:
        db_path = r'C:\Users\metin\Desktop\BRIC\app\www\hands_database.json'
        
        print(f"\n{'=' * 70}")
        print("💾 Saving database...")
        
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(all_boards, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Database saved!")
        print(f"   Location: {db_path}")
        print(f"   Total boards: {len(all_boards)}")
        
        # Summary by date
        print(f"\n📊 Summary by Date:")
        boards_by_date = {}
        for board in all_boards.values():
            date = board['date']
            if date not in boards_by_date:
                boards_by_date[date] = 0
            boards_by_date[date] += 1
        
        for date in sorted(boards_by_date.keys()):
            print(f"   {date}: {boards_by_date[date]} boards")
    else:
        print(f"\n❌ No boards fetched!")

if __name__ == '__main__':
    main()
