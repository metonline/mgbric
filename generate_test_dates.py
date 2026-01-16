#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import random

# Create test hands with specific dates
def generate_hands_for_dates():
    """Generate hands data with specific test dates including 03.01.2026"""
    
    hands_data = {
        "events": {},
        "metadata": {
            "total_events": 0,
            "total_boards": 0,
            "generated": "2026-01-04T04:00:00"
        }
    }
    
    # Dates to generate (including 03.01.2026)
    test_dates = [
        "03.01.2026",
        "02.01.2026", 
        "01.01.2026",
        "31.12.2025",
        "30.12.2025",
        "29.12.2025"
    ]
    
    event_count = 0
    board_count = 0
    
    # Create 3 tournaments per date
    for date in test_dates:
        for i in range(3):
            event_key = f"event_{date.replace('.', '_')}_{i+1}"
            tournament_name = f"Turnuva {date} - {i+1}"
            
            hands_data["events"][event_key] = {
                "date": date,
                "name": tournament_name,
                "location": "Hoşgörü Kulübü",
                "boards": generate_boards(8)  # 8 boards per tournament
            }
            
            board_count += 8
            event_count += 1
            print(f"Created: {event_key}")
    
    hands_data["metadata"]["total_events"] = event_count
    hands_data["metadata"]["total_boards"] = board_count
    
    # Save
    with open('app/www/hands_database.json', 'w', encoding='utf-8') as f:
        json.dump(hands_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Generated hands_database.json")
    print(f"  Total Events: {event_count}")
    print(f"  Total Boards: {board_count}")
    print(f"  File size: {len(json.dumps(hands_data)) / 1024:.2f} KB")
    print(f"\nTest dates:")
    for date in test_dates:
        print(f"  - {date}")

def generate_boards(count):
    """Generate sample board data"""
    boards = {}
    
    for board_num in range(1, count + 1):
        boards[str(board_num)] = {
            "board_number": board_num,
            "dealer": random.choice(['N', 'E', 'S', 'W']),
            "vulnerability": random.choice(['None', 'NS', 'EW', 'Both']),
            "hands": {
                "North": random.sample(['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2'], k=13),
                "South": random.sample(['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2'], k=13),
                "East": random.sample(['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2'], k=13),
                "West": random.sample(['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2'], k=13)
            },
            "result": {
                "contract": f"{random.randint(1, 7)}{random.choice(['NT', 'S', 'H', 'D', 'C'])}",
                "declarer": random.choice(['N', 'S', 'E', 'W']),
                "tricks": random.randint(6, 13),
                "points": random.randint(0, 1500)
            }
        }
    
    return boards

if __name__ == '__main__':
    print("Generating test hands with specific dates...\n")
    generate_hands_for_dates()
    print("\nReload http://localhost:8000/app/www/ and try selecting 03.01.2026")
