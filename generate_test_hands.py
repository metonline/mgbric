#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import random
from datetime import datetime, timedelta

# Sample bridge hands data generator
def generate_hands_data():
    """Generate test bridge hands data for 3,126 tournaments"""
    
    hands_data = {
        "events": {},
        "metadata": {
            "total_events": 0,
            "total_boards": 0,
            "generated": datetime.now().isoformat()
        }
    }
    
    # Load existing database to use tournament dates
    try:
        with open('database.json', 'r', encoding='utf-8') as f:
            tournaments = json.load(f)
    except:
        tournaments = []
    
    event_count = 0
    board_count = 0
    
    # Create hands for each tournament
    for tournament in tournaments[:3126]:  # Limit to 3,126
        try:
            date = tournament.get('Tarih', '01.01.2025')
            event_key = f"event_{date.replace('.', '_')}_{event_count}"
            tournament_name = tournament.get('Turnuva Adı', 'Turnuva')
            
            hands_data["events"][event_key] = {
                "date": date,
                "name": tournament_name,
                "location": "Hoşgörü Kulübü",
                "boards": generate_boards(15)  # 15 boards per tournament
            }
            
            board_count += 15
            event_count += 1
            
            if event_count % 500 == 0:
                print(f"Generated {event_count} tournaments...")
        except Exception as e:
            print(f"Error processing tournament: {e}")
            continue
    
    hands_data["metadata"]["total_events"] = event_count
    hands_data["metadata"]["total_boards"] = board_count
    
    # Save to hands_database.json
    with open('app/www/hands_database.json', 'w', encoding='utf-8') as f:
        json.dump(hands_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Generated hands_database.json")
    print(f"  Total Events: {event_count}")
    print(f"  Total Boards: {board_count}")
    print(f"  File size: {len(json.dumps(hands_data)) / 1024 / 1024:.2f} MB")

def generate_boards(count):
    """Generate sample board data"""
    boards = {}
    
    suits = ['♠', '♥', '♦', '♣']
    ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
    
    for board_num in range(1, count + 1):
        # Generate random hands
        north_hand = generate_hand()
        south_hand = generate_hand()
        east_hand = generate_hand()
        west_hand = generate_hand()
        
        boards[str(board_num)] = {
            "board_number": board_num,
            "dealer": random.choice(['N', 'E', 'S', 'W']),
            "vulnerability": random.choice(['None', 'NS', 'EW', 'Both']),
            "hands": {
                "North": north_hand,
                "South": south_hand,
                "East": east_hand,
                "West": west_hand
            },
            "result": {
                "contract": f"{random.randint(1, 7)}{random.choice(['NT', 'S', 'H', 'D', 'C'])}",
                "declarer": random.choice(['N', 'S', 'E', 'W']),
                "tricks": random.randint(6, 13),
                "points": random.randint(0, 1500)
            }
        }
    
    return boards

def generate_hand():
    """Generate a random bridge hand"""
    suits = ['Spades', 'Hearts', 'Diamonds', 'Clubs']
    ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
    
    hand = {}
    remaining = list(range(52))
    
    for suit in suits:
        hand[suit] = random.sample(ranks, k=random.randint(0, 13))
    
    return hand

if __name__ == '__main__':
    print("Generating test hands data...")
    print("This may take a moment...\n")
    generate_hands_data()
    print("\nDone! Open http://localhost:8000/app/www/ and test the hands viewer.")
