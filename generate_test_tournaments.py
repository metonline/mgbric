#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate test tournament data for missing dates
Creates tournament hands data for dates between 01.01.26 and 07.01.26
"""

import json
import os
from datetime import datetime, timedelta

def load_existing_hands():
    """Load the existing hands database"""
    db_path = r'C:\Users\metin\Desktop\BRIC\app\www\hands_database.json'
    
    if os.path.exists(db_path):
        with open(db_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def create_tournament_data():
    """Create tournament data for missing dates"""
    
    # Load existing hands (from 04.01.26)
    existing_hands = load_existing_hands()
    print(f"✓ Loaded {len(existing_hands)} existing boards from 04.01.26")
    
    # Create new database with tournament metadata structure
    new_database = {}
    board_counter = 1
    
    # Dates with tournaments
    tournament_dates = [
        ('2026-01-01', 'PAZAR ÖĞLEDENSONRASı TURNUVASI'),
        ('2026-01-02', 'CUMA AKŞAM TURNUVASI'),
        ('2026-01-03', 'CUMARTESİ GÜNÜ TURNUVASI'),
        ('2026-01-04', 'PAZAR SİMULTANE'),  # Original date
        ('2026-01-05', 'PAZARTESI TURNUVASI'),
        ('2026-01-06', 'SALI TURNUVASI'),
        ('2026-01-07', 'ÇARŞAMBA TURNUVASI'),
    ]
    
    # Create tournaments for each date
    for date_str, tournament_name in tournament_dates:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        date_formatted = date_obj.strftime('%Y-%m-%d')  # Keep as YYYY-MM-DD for JavaScript
        
        print(f"\n📅 Creating tournament for {date_formatted}: {tournament_name}")
        
        # Create 2-3 boards per tournament (reuse hands data)
        num_boards = 3 if date_str != '2026-01-04' else 30  # Keep original tournament at 30
        hands_to_use = list(existing_hands.values())[:num_boards]
        
        for i, hands in enumerate(hands_to_use, 1):
            board_key = str(board_counter)
            new_database[board_key] = {
                'date': date_formatted,
                'tournament': tournament_name,
                'board_num': i,
                'N': hands.get('N', {}),
                'S': hands.get('S', {}),
                'E': hands.get('E', {}),
                'W': hands.get('W', {})
            }
            board_counter += 1
        
        print(f"   Added {num_boards} boards")
    
    return new_database

def save_database(database):
    """Save the new database"""
    db_path = r'C:\Users\metin\Desktop\BRIC\app\www\hands_database.json'
    
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Database saved with {len(database)} total boards")
    print(f"   Location: {db_path}")

def main():
    print("=" * 60)
    print("🎯 Test Tournament Data Generator")
    print("=" * 60)
    
    print("\nGenerating tournament data for:")
    print("  • 01.01.2026 - PAZAR ÖĞLEDENSONRASı TURNUVASI")
    print("  • 02.01.2026 - CUMA AKŞAM TURNUVASI")
    print("  • 03.01.2026 - CUMARTESİ GÜNÜ TURNUVASI")
    print("  • 04.01.2026 - PAZAR SİMULTANE (existing)")
    print("  • 05.01.2026 - PAZARTESI TURNUVASI")
    print("  • 06.01.2026 - SALI TURNUVASI")
    print("  • 07.01.2026 - ÇARŞAMBA TURNUVASI")
    
    new_db = create_tournament_data()
    save_database(new_db)
    
    # Show summary
    dates = set()
    tournaments = {}
    
    for board_data in new_db.values():
        date = board_data['date']
        dates.add(date)
        tournament = board_data['tournament']
        
        if tournament not in tournaments:
            tournaments[tournament] = {'date': date, 'count': 0}
        tournaments[tournament]['count'] += 1
    
    print("\n" + "=" * 60)
    print("📊 Summary:")
    print(f"   Total dates: {len(dates)}")
    print(f"   Total tournaments: {len(tournaments)}")
    print(f"   Total boards: {len(new_db)}")
    print("\n📋 Tournament Breakdown:")
    
    for tournament, info in sorted(tournaments.items()):
        print(f"   • {info['date']}: {tournament} ({info['count']} boards)")

if __name__ == '__main__':
    main()
