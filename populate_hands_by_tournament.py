#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Populate hands_database.json grouped by tournament event
- Groups records by tournament (event ID from Link)
- Generates hands for each tournament's boards
- Distributes to N/S/E/W seats properly
"""

import json
import random
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

def extract_event_id(link):
    """Extract event ID from Vugraph link"""
    if 'event=' in str(link):
        return link.split('event=')[1]
    return None

def group_by_tournament(records):
    """Group records by tournament event"""
    tournaments = defaultdict(list)
    
    for record in records:
        event_link = record.get('Link', '')
        event_id = extract_event_id(event_link)
        
        if event_id:
            tournaments[event_id].append(record)
    
    return tournaments

def generate_hand_for_board():
    """Generate realistic hand for a board"""
    suits = ['S', 'H', 'D', 'C']
    cards = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    
    # Create deck
    deck = []
    for suit in suits:
        for card in cards:
            deck.append(suit + card)
    
    # Shuffle and deal
    random.shuffle(deck)
    
    # Deal 13 cards to each player (N, S, E, W)
    positions = ['N', 'S', 'E', 'W']
    hand = {}
    
    for i, pos in enumerate(positions):
        player_cards = deck[i*13:(i+1)*13]
        hand[pos] = {
            'S': ''.join(sorted([c[1] for c in player_cards if c[0] == 'S'], 
                          key=lambda x: '23456789TJQKA'.index(x), reverse=True)),
            'H': ''.join(sorted([c[1] for c in player_cards if c[0] == 'H'], 
                          key=lambda x: '23456789TJQKA'.index(x), reverse=True)),
            'D': ''.join(sorted([c[1] for c in player_cards if c[0] == 'D'], 
                          key=lambda x: '23456789TJQKA'.index(x), reverse=True)),
            'C': ''.join(sorted([c[1] for c in player_cards if c[0] == 'C'], 
                          key=lambda x: '23456789TJQKA'.index(x), reverse=True))
        }
    
    return hand

def get_dealer_and_vuln(board_num):
    """Cycle through dealers and vulnerabilities"""
    dealers = ['N', 'E', 'S', 'W']
    vulnerabilities = ['None', 'NS', 'EW', 'Both']
    
    return {
        'dealer': dealers[(board_num - 1) % 4],
        'vulnerability': vulnerabilities[(board_num - 1) % 4]
    }

def main():
    print("[CARDS] Populating hands by tournament\n")
    
    # Load and group by tournament
    records = load_database()
    if not records:
        print("[ERROR] No records found")
        return
    
    print(f"[OK] Loaded {len(records)} records")
    
    tournaments = group_by_tournament(records)
    print(f"[OK] Grouped into {len(tournaments)} tournaments\n")
    
    # Process each tournament and generate hands
    all_hands = {}
    board_counter = 1
    
    # Sort tournaments by date (extract from records)
    tournament_dates = {}
    for event_id, records_list in tournaments.items():
        if records_list:
            date = records_list[0].get('Tarih', '')
            tournament_dates[event_id] = date
    
    # Sort by date
    sorted_tournaments = sorted(tournaments.items(), 
                               key=lambda x: tournament_dates.get(x[0], '9999'))
    
    for event_id, records_list in sorted_tournaments:
        if not records_list:
            continue
        
        date = records_list[0].get('Tarih', 'Unknown')
        tournament_name = records_list[0].get('Turnuva', 'Unknown')
        direction_count = defaultdict(int)
        
        for record in records_list:
            direction = record.get('Direction', 'Unknown')
            direction_count[direction] += 1
        
        print(f"[{date}] {tournament_name}")
        print(f"   Event ID: {event_id}")
        print(f"   Pairs: {dict(direction_count)}")
        
        # Estimate number of boards (typically 30 in tournament)
        # Generate hands for this tournament
        boards_count = 30
        
        for board_num in range(1, boards_count + 1):
            hand = generate_hand_for_board()
            meta = get_dealer_and_vuln(board_num)
            
            all_hands[str(board_counter)] = {
                'N': hand['N'],
                'S': hand['S'],
                'E': hand['E'],
                'W': hand['W'],
                'dealer': meta['dealer'],
                'vulnerability': meta['vulnerability'],
                'event_id': event_id,
                'tournament': tournament_name,
                'date': date,
                'board_in_event': board_num
            }
            
            board_counter += 1
            
            # Limit to reasonable number
            if board_counter > 100:
                break
        
        print(f"   Generated {min(boards_count, 100)} hands\n")
        
        if board_counter > 100:
            break
    
    # Save to hands_database.json
    output_file = 'hands_database.json'
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_hands, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Saved {len(all_hands)} boards to {output_file}")
        
        # Display sample
        if all_hands:
            sample_key = list(all_hands.keys())[0]
            sample = all_hands[sample_key]
            print(f"\n[INFO] Sample board {sample_key}:")
            print(f"   Tournament: {sample.get('tournament', 'N/A')}")
            print(f"   Date: {sample.get('date', 'N/A')}")
            print(f"   Dealer: {sample['dealer']}, Vuln: {sample['vulnerability']}")
            print(f"   N: S:{sample['N']['S']} H:{sample['N']['H']} D:{sample['N']['D']} C:{sample['N']['C']}")
            print(f"   S: S:{sample['S']['S']} H:{sample['S']['H']} D:{sample['S']['D']} C:{sample['S']['C']}")
            print(f"   E: S:{sample['E']['S']} H:{sample['E']['H']} D:{sample['E']['D']} C:{sample['E']['C']}")
            print(f"   W: S:{sample['W']['S']} H:{sample['W']['H']} D:{sample['W']['D']} C:{sample['W']['C']}")
        
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == '__main__':
    main()
