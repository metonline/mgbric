#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Populate hands_database.json with actual tournament hands from database.json
- Maps tournament hands to their correct N/S/E/W seats
- Only includes 2026 tournaments (one per day, 16 max)
"""

import json
import os
from collections import defaultdict
from datetime import datetime

def load_database():
    """Load tournament database"""
    try:
        with open('database.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading database: {e}")
        return []

def parse_hand_from_tournament(board_data):
    """Extract and parse hand data from tournament record"""
    # Tournament records might have hand info in different formats
    # Try to extract N/S/E/W hands if available
    
    hands = {
        'N': {'S': '', 'H': '', 'D': '', 'C': ''},
        'S': {'S': '', 'H': '', 'D': '', 'C': ''},
        'E': {'S': '', 'H': '', 'D': '', 'C': ''},
        'W': {'S': '', 'H': '', 'D': '', 'C': ''}
    }
    
    # Check for hands in record
    if 'hands' in board_data:
        hands_data = board_data['hands']
        if isinstance(hands_data, dict):
            for direction in ['N', 'S', 'E', 'W']:
                if direction in hands_data:
                    hand = hands_data[direction]
                    if isinstance(hand, dict):
                        for suit in ['S', 'H', 'D', 'C']:
                            hands[direction][suit] = hand.get(suit, '')
    
    return hands

def group_tournaments_by_date(records):
    """Group tournament records by date, one tournament per day"""
    by_date = defaultdict(list)
    
    for record in records:
        date = record.get('date', '')
        if date and '2026' in str(date):  # Only 2026
            by_date[date].append(record)
    
    return by_date

def extract_boards_from_tournament(tournament_records):
    """Extract board-level hands from tournament records"""
    boards = {}
    
    for record in tournament_records:
        board_num = record.get('board', record.get('board_num', ''))
        if not board_num:
            continue
            
        board_num = str(board_num)
        
        # Only keep first occurrence of each board
        if board_num in boards:
            continue
        
        hands = parse_hand_from_tournament(record)
        
        # Check if we got valid hand data
        has_hand_data = any(
            any(hands[pos][suit] for suit in ['S', 'H', 'D', 'C'])
            for pos in ['N', 'S', 'E', 'W']
        )
        
        if has_hand_data:
            boards[board_num] = {
                'N': hands['N'],
                'S': hands['S'],
                'E': hands['E'],
                'W': hands['W'],
                'dealer': record.get('dealer', 'N'),
                'vulnerability': record.get('vulnerability', 'None')
            }
    
    return boards

def main():
    print("📊 Populating hands_database.json from tournament data\n")
    
    # Load tournament database
    db = load_database()
    if not db:
        print("❌ No tournament database found")
        return
    
    print(f"✅ Loaded {len(db)} tournament records")
    
    # Group by date
    by_date = group_tournaments_by_date(db)
    print(f"✅ Found tournaments on {len(by_date)} dates in 2026")
    
    # Extract hands for each date
    all_hands = {}
    board_counter = 1
    
    for date in sorted(by_date.keys()):
        tournament_records = by_date[date]
        boards = extract_boards_from_tournament(tournament_records)
        
        if boards:
            print(f"\n📅 {date}: {len(boards)} boards found")
            
            # Assign board numbers sequentially across all tournaments
            for board_num in sorted(boards.keys(), key=lambda x: int(x) if x.isdigit() else 999):
                all_hands[str(board_counter)] = boards[board_num]
                print(f"   Board {board_counter}: #{board_num} from tournament")
                board_counter += 1
        else:
            print(f"\n📅 {date}: ⚠️ No valid hand data found")
    
    # Save to hands_database.json
    output_file = 'hands_database.json'
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_hands, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Successfully saved {len(all_hands)} boards to {output_file}")
        
        # Display summary
        if all_hands:
            sample_board = list(all_hands.values())[0]
            print("\n📋 Sample board structure:")
            print(f"   North:  {sample_board['N']}")
            print(f"   South:  {sample_board['S']}")
            print(f"   East:   {sample_board['E']}")
            print(f"   West:   {sample_board['W']}")
            print(f"   Dealer: {sample_board.get('dealer', 'N')}")
            print(f"   Vuln:   {sample_board.get('vulnerability', 'None')}")
        
    except Exception as e:
        print(f"❌ Error saving file: {e}")

if __name__ == '__main__':
    main()
