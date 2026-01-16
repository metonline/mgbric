#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch real tournament data from Vugraph for dates 01.01.26 - 07.01.26
Searches for available tournaments and fetches their board data
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import os
from datetime import datetime, timedelta

def find_tournaments_on_date(date_str):
    """
    Find all tournaments available on a specific date from Vugraph
    date_str format: YYYY-MM-DD
    """
    print(f"\n🔍 Searching for tournaments on {date_str}...")
    
    tournaments = []
    
    try:
        # Try different URL patterns for Vugraph
        # Pattern 1: Direct event listing
        url = f"https://clubs.vugraph.com/hosgoru/eventresults.php?event=&date={date_str}"
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for event links
        event_links = soup.find_all('a', href=re.compile(r'event=\d+'))
        
        found_events = set()
        for link in event_links:
            href = link['href']
            match = re.search(r'event=(\d+)', href)
            if match:
                event_id = int(match.group(1))
                if event_id not in found_events:
                    found_events.add(event_id)
                    tournament_name = link.get_text().strip()
                    tournaments.append({
                        'event_id': event_id,
                        'name': tournament_name,
                        'date': date_str
                    })
        
        if tournaments:
            print(f"   ✅ Found {len(tournaments)} tournament(s):")
            for t in tournaments:
                print(f"      Event {t['event_id']}: {t['name']}")
        else:
            print(f"   ⚠️  No tournaments found on {date_str}")
    
    except Exception as e:
        print(f"   ❌ Error searching for tournaments: {e}")
    
    return tournaments

def fetch_boards_from_event(event_id, max_boards=100):
    """
    Fetch all boards from a specific event
    """
    print(f"\n📥 Fetching boards from event {event_id}...")
    
    boards = {}
    consecutive_failures = 0
    
    for board_num in range(1, max_boards + 1):
        try:
            url = f"https://clubs.vugraph.com/hosgoru/boardsummary.php?event={event_id}&board={board_num}"
            response = requests.get(url, timeout=10)
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text()
            
            # Look for hand patterns
            hand_pattern = r'[SHDCN]:[A-Z0-9]+'
            hands_found = re.findall(hand_pattern, text)
            
            if hands_found:
                # Extract dealer and vulnerability
                dealer_match = re.search(r'[Dd]ealer\s*[:\s]+([NEWS])', text)
                dealer = dealer_match.group(1).upper() if dealer_match else 'N'
                
                vuln_match = re.search(r'[Vv]uln[a-z]*\s*[:\s]+([^,\n]+)', text)
                vulnerability = vuln_match.group(1).strip() if vuln_match else '-'
                
                boards[str(board_num)] = {
                    'dealer': dealer,
                    'vulnerability': vulnerability,
                    'hands_text': hands_found
                }
                
                consecutive_failures = 0
                if board_num % 5 == 0:
                    print(f"   Fetched {board_num} boards...")
            else:
                consecutive_failures += 1
                if consecutive_failures > 10:
                    print(f"   Stopping at board {board_num} (no more hands found)")
                    break
        
        except Exception as e:
            consecutive_failures += 1
            if consecutive_failures > 10:
                break
    
    print(f"   ✅ Fetched {len(boards)} boards from event {event_id}")
    return boards

def fetch_all_tournaments_in_range(start_date, end_date):
    """
    Fetch all tournaments in a date range
    Dates in YYYY-MM-DD format
    """
    print("=" * 60)
    print("🌉 Real Tournament Data Fetcher (Vugraph)")
    print("=" * 60)
    
    all_tournaments = {}
    current_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    
    while current_date <= end_date_obj:
        date_str = current_date.strftime('%Y-%m-%d')
        
        tournaments = find_tournaments_on_date(date_str)
        
        for tournament in tournaments:
            key = f"{tournament['event_id']}_{tournament['date']}"
            all_tournaments[key] = tournament
        
        current_date += timedelta(days=1)
    
    return all_tournaments

def main():
    print("\n📋 Fetching real tournament data from Vugraph...")
    print("   Date range: 01.01.2026 - 07.01.2026\n")
    
    # Fetch available tournaments
    tournaments = fetch_all_tournaments_in_range('2026-01-01', '2026-01-07')
    
    if not tournaments:
        print("\n⚠️  No tournaments found on Vugraph for 01-07 January 2026")
        print("\n💡 Known tournaments:")
        print("   • Event 404377: PAZAR SİMULTANE (04-01-2026)")
        print("\n📌 To fetch from a specific event ID, use:")
        print("   python fetch_vugraph_hands.py")
        return
    
    print(f"\n✅ Found {len(tournaments)} tournament(s)")
    print("\n📋 Tournaments to fetch:")
    for key, tournament in sorted(tournaments.items()):
        print(f"   • Event {tournament['event_id']}: {tournament['name']} ({tournament['date']})")
    
    # Ask user to confirm
    confirm = input("\n🔄 Fetch boards from these tournaments? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("Cancelled.")
        return
    
    # Fetch boards and create new database
    new_database = {}
    board_counter = 1
    
    for key, tournament in sorted(tournaments.items()):
        event_id = tournament['event_id']
        date_str = tournament['date']
        
        boards = fetch_boards_from_event(event_id)
        
        if boards:
            for board_num, board_data in boards.items():
                board_key = str(board_counter)
                new_database[board_key] = {
                    'date': date_str,
                    'tournament': tournament['name'],
                    'board_num': int(board_num),
                    'dealer': board_data['dealer'],
                    'vulnerability': board_data['vulnerability'],
                    'N': {},
                    'S': {},
                    'E': {},
                    'W': {}
                }
                board_counter += 1
    
    if new_database:
        # Save database
        db_path = r'C:\Users\metin\Desktop\BRIC\app\www\hands_database.json'
        
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(new_database, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Database saved!")
        print(f"   Location: {db_path}")
        print(f"   Total boards: {len(new_database)}")
        print(f"\n💾 Note: Board hands text extracted but needs detailed parsing")
        print(f"   Consider using fetch_vugraph_hands.py for complete board details")
    else:
        print("\n❌ No boards fetched")

if __name__ == '__main__':
    main()
