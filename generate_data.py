#!/usr/bin/env python3
"""Generate comprehensive bridge hands database with 03.01.2026 date"""
import json
from datetime import datetime, timedelta
import random

RANKS = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
SUITS = ['S', 'H', 'D', 'C']
DEALERS = ['N', 'S', 'E', 'W']
VULNERABILITIES = ['None', 'NS', 'EW', 'Both']

def create_full_deal():
    """Create a complete random deal"""
    all_cards = []
    for suit in SUITS:
        all_cards.extend([suit + rank for rank in RANKS])
    
    random.shuffle(all_cards)
    
    hands = {}
    positions = ['North', 'South', 'East', 'West']
    for i, pos in enumerate(positions):
        hand = {}
        cards = sorted(all_cards[i*13:(i+1)*13])
        
        for suit in SUITS:
            suit_cards = [c[1] for c in cards if c[0] == suit]
            suit_cards.sort(key=lambda x: RANKS.index(x))
            hand[suit] = ''.join(suit_cards)
        
        hands[pos] = hand
    
    return hands

# Create events
events = {}

# Create 6 tournaments for 03.01.2026
for day_offset in [0, 1, 2, 3]:
    date_obj = datetime(2026, 1, 3) + timedelta(days=day_offset)
    date_str = date_obj.strftime("%d.%m.%Y")
    
    tournaments_per_day = 3
    for t in range(tournaments_per_day):
        event_key = f"event_{date_str.replace('.', '_')}_{t+1}"
        
        boards = {}
        for board_num in range(1, 9):  # 8 boards per tournament
            hands = create_full_deal()
            
            board = {
                "dealer": DEALERS[(board_num - 1) % 4],
                "vulnerability": VULNERABILITIES[(board_num - 1) % 4],
                "hands": hands,
                "result": {
                    "contract": random.choice(["1NT", "2NT", "3NT", "7NT", "6NT", "4S", "4H", "5D", "5C", "Pass"]),
                    "tricks": random.randint(6, 13),
                    "result": "made" if random.random() > 0.3 else "failed"
                }
            }
            boards[str(board_num)] = board
        
        events[event_key] = {
            "name": f"Tournament {t+1} ({date_str})",
            "date": date_str,
            "location": "Istanbul",
            "boards": boards
        }

# Write database
output_path = "app/www/hands_database.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump({"events": events}, f, indent=2, ensure_ascii=False)

total_boards = sum(len(e['boards']) for e in events.values())
print(f"Database created: {output_path}")
print(f"Total events: {len(events)}")
print(f"Total boards: {total_boards}")
print(f"Date range: 03.01.2026 to 06.01.2026")
