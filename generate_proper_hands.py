#!/usr/bin/env python3
"""Generate bridge hands database with proper suit organization"""
import json
from datetime import datetime, timedelta
import random

# Card rank order (high to low)
RANKS = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
SUITS = ['S', 'H', 'D', 'C']  # Spade, Heart, Diamond, Club
DEALERS = ['N', 'S', 'E', 'W']
VULNERABILITIES = ['None', 'NS', 'EW', 'Both']
POSITIONS = ['North', 'South', 'East', 'West']

def create_hand_for_position():
    """Create a properly organized hand with suits and ranked cards"""
    hand = {}
    available_cards = set()
    
    # Create all 52 cards
    for suit in SUITS:
        for rank in RANKS:
            available_cards.add(suit + rank)
    
    # Distribute 13 cards to this hand
    distributed = random.sample(list(available_cards), 13)
    
    # Organize by suit
    for suit in SUITS:
        cards_in_suit = [card[1] for card in distributed if card[0] == suit]
        # Sort by rank (RANKS order)
        cards_in_suit.sort(key=lambda c: RANKS.index(c))
        if cards_in_suit:
            hand[suit] = ''.join(cards_in_suit)
        else:
            hand[suit] = ''
    
    return hand

def create_full_deal():
    """Create a complete deal for 4 hands (removing duplicates)"""
    all_cards = []
    for suit in SUITS:
        all_cards.extend([suit + rank for rank in RANKS])
    
    # Shuffle cards
    random.shuffle(all_cards)
    
    # Distribute to 4 players
    hands = {}
    idx = 0
    for position in POSITIONS:
        hand = {}
        player_cards = all_cards[idx:idx+13]
        
        # Organize by suit
        for suit in SUITS:
            cards_in_suit = [card[1] for card in player_cards if card[0] == suit]
            cards_in_suit.sort(key=lambda c: RANKS.index(c))
            if cards_in_suit:
                hand[suit] = ''.join(cards_in_suit)
            else:
                hand[suit] = ''
        
        hands[position] = hand
        idx += 13
    
    return hands

def generate_database():
    """Generate complete bridge hands database"""
    events = {}
    
    # Create 6 different dates
    base_date = datetime(2026, 1, 3)
    dates = [(base_date - timedelta(days=i)).strftime("%d.%m.%Y") for i in range(6)]
    
    event_id = 1
    for date in dates:
        # 3 tournaments per date
        for tour_num in range(1, 4):
            tournament_name = f"Turnuva {date} - {tour_num}"
            event_key = f"event_{date.replace('.', '_')}_{tour_num}"
            
            # 8 boards per tournament
            boards = {}
            for board_num in range(1, 9):
                hands = create_full_deal()
                
                boards[str(board_num)] = {
                    "board_number": board_num,
                    "dealer": random.choice(DEALERS),
                    "vulnerability": random.choice(VULNERABILITIES),
                    "hands": hands,
                    "result": {
                        "contract": f"{random.randint(1, 7)}{random.choice(['NT', 'S', 'H', 'D', 'C'])}",
                        "declarer": random.choice(['N', 'S', 'E', 'W']),
                        "tricks": random.randint(6, 13),
                        "points": random.randint(100, 1000)
                    }
                }
            
            events[event_key] = {
                "date": date,
                "name": tournament_name,
                "location": "Hoşgörü Kulübü",
                "boards": boards
            }
            event_id += 1
    
    return {"events": events}

if __name__ == "__main__":
    print("Generating bridge hands database with proper suit organization...")
    database = generate_database()
    
    # Save to file
    with open('app/www/hands_database.json', 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Database generated!")
    print(f"   Events: {len(database['events'])}")
    
    # Show example
    first_event = list(database['events'].values())[0]
    first_board = first_event['boards']['1']
    print(f"\n📋 Example Board:")
    print(f"   Date: {first_event['date']}")
    print(f"   Tournament: {first_event['name']}")
    print(f"   Board 1 - Dealer: {first_board['dealer']}, Vuln: {first_board['vulnerability']}")
    print(f"\n   North hand:")
    for suit in ['S', 'H', 'D', 'C']:
        print(f"      {suit}: {first_board['hands']['North'][suit]}")
    print(f"\n   South hand:")
    for suit in ['S', 'H', 'D', 'C']:
        print(f"      {suit}: {first_board['hands']['South'][suit]}")
