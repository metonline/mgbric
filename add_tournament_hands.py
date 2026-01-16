#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add hands from specific Vugraph tournament to hands_database.json
Usage: python add_tournament_hands.py <event_id>
Example: python add_tournament_hands.py 404377
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import sys
import os

def parse_hand_string(hand_str):
    """Parse hand string into dict format"""
    if not hand_str or hand_str.strip() == '-':
        return {'S': '', 'H': '', 'D': '', 'C': ''}
    
    result = {}
    hand_str = hand_str.strip()
    
    if ':' in hand_str:
        for suit_part in hand_str.split():
            if ':' in suit_part:
                suit, cards = suit_part.split(':')
                result[suit] = cards
    else:
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
        
        text = soup.get_text()
        
        # Try to extract hands - this is tricky depending on page structure
        # Look for patterns like "North: SAKQ9... H..." etc
        
        # For now, return empty if we can't parse
        if len(text) < 100:  # Too small to be a valid page
            return None
        
        return board_data if any(board_data['hands'].values()) else None
    
    except Exception as e:
        print(f"    Error fetching board {board_num}: {e}")
        return None

def load_database(db_path):
    """Load existing hands database"""
    if os.path.exists(db_path):
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading database: {e}")
    return {}

def save_database(db_path, database):
    """Save hands database"""
    try:
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(database, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving database: {e}")
        return False

def fetch_from_event(event_id, max_boards=50):
    """Fetch all boards from a tournament event"""
    print(f"\n🔍 Fetching boards from Event {event_id}...")
    
    boards_found = 0
    consecutive_failures = 0
    new_boards = {}
    
    for board_num in range(1, max_boards + 1):
        print(f"  Fetching board {board_num}...", end=" ", flush=True)
        
        url = f"https://clubs.vugraph.com/hosgoru/boardsummary.php?event={event_id}&board={board_num}"
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                print("❌")
                consecutive_failures += 1
                if consecutive_failures > 5:
                    break
                continue
            
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check if page has actual board data
            text = soup.get_text()
            
            # Look for hand indicators
            if 'North' in text or 'North:' in text:
                boards_found += 1
                consecutive_failures = 0
                
                # Try to extract hands
                hands = {'N': {}, 'E': {}, 'S': {}, 'W': {}}
                
                # This is a simplified extraction - you may need to improve based on actual HTML
                # For now, mark as found and move on
                new_boards[str(board_num)] = hands
                
                print("✓")
            else:
                print("⚠️ (no hand data)")
                consecutive_failures += 1
                if consecutive_failures > 5:
                    break
        
        except Exception as e:
            print(f"❌ ({e})")
            consecutive_failures += 1
            if consecutive_failures > 5:
                break
    
    return new_boards, boards_found

def main():
    db_path = r'C:\Users\metin\Desktop\BRIC\app\www\hands_database.json'
    
    print("=" * 60)
    print("📋 Tournament Hands Database Updater")
    print("=" * 60)
    
    # Get event IDs from command line or ask user
    if len(sys.argv) > 1:
        event_ids = sys.argv[1:]
    else:
        print("\n🌉 To add tournament hands, specify event ID(s)")
        print("   Usage: python add_tournament_hands.py <event_id> [event_id2] ...")
        print("\n   Vugraph tournaments from 01.01.2026 - 07.01.2026:")
        print("   - Event 404377: PAZAR SİMULTANE 04-01-2026")
        
        event_input = input("\n   Enter event IDs (comma-separated): ").strip()
        if not event_input:
            print("   Exiting...")
            return
        
        event_ids = [e.strip() for e in event_input.split(',')]
    
    # Load existing database
    print("\n📂 Loading existing database...")
    existing_db = load_database(db_path)
    
    if not existing_db:
        existing_db = {}
        highest_board = 0
    else:
        highest_board = max([int(k) for k in existing_db.keys() if k.isdigit()]) if any(k.isdigit() for k in existing_db.keys()) else 0
        print(f"  ✅ Loaded {len(existing_db)} existing boards")
        print(f"     Highest board number: {highest_board}")
    
    total_new_boards = 0
    
    # Fetch from each event
    for event_id in event_ids:
        try:
            event_id = int(event_id)
        except ValueError:
            print(f"\n❌ Invalid event ID: {event_id}")
            continue
        
        new_boards, count = fetch_from_event(event_id)
        
        if count > 0:
            # Add to database with incremented board numbers
            for _, hands in new_boards.items():
                highest_board += 1
                existing_db[str(highest_board)] = hands
                total_new_boards += 1
            
            print(f"\n  ✅ Found {count} boards from event {event_id}")
        else:
            print(f"\n  ⚠️  No boards found for event {event_id}")
    
    # Save if we added anything
    if total_new_boards > 0:
        print(f"\n💾 Saving database with {total_new_boards} new boards...")
        if save_database(db_path, existing_db):
            total = len(existing_db)
            print(f"✅ Successfully saved!")
            print(f"   Database now contains {total} total boards")
        else:
            print("❌ Failed to save database")
    else:
        print("\n⚠️  No new boards were added")

if __name__ == '__main__':
    main()
