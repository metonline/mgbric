#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch missing hands from vugraph for all boards
Populates hands_database.json with hands from all tournament boards
"""

import json
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from time import sleep
import re

BOARD_RESULTS_PATH = Path(__file__).parent / "board_results.json"
HANDS_DB_PATH = Path(__file__).parent / "hands_database.json"

# Existing hands from database
with open(HANDS_DB_PATH, 'r', encoding='utf-8-sig') as f:
    existing_hands = json.load(f)

# Convert to dict for easier lookup
hands_dict = {}
if isinstance(existing_hands, list):
    for hand in existing_hands:
        key = f"{hand.get('event')}_{hand.get('board')}"
        hands_dict[key] = hand

print(f"Loaded {len(hands_dict)} existing hand records")

# Load board results to get all boards we need hands for
with open(BOARD_RESULTS_PATH, 'r', encoding='utf-8-sig') as f:
    board_data = json.load(f)

# Get list of all boards we need
needed_boards = {}
if 'boards' in board_data:
    for board_key, board_info in board_data['boards'].items():
        event_id = board_info.get('event_id', '')
        board_num = board_info.get('board', 0)
        
        key = f"{event_id}_{board_num}"
        if key not in hands_dict:
            if event_id not in needed_boards:
                needed_boards[event_id] = []
            needed_boards[event_id].append(board_num)

print(f"\nNeed to fetch hands for {sum(len(b) for b in needed_boards.values())} boards")
for event_id in sorted(needed_boards.keys()):
    print(f"  Event {event_id}: boards {sorted(needed_boards[event_id])}")

# Function to calculate dealer and vulnerability
def get_dealer(board_num):
    dealer_cycle = (board_num - 1) % 4
    dealers = ['N', 'E', 'S', 'W']
    return dealers[dealer_cycle]

def get_vuln(board_num):
    cycle_pos = ((board_num - 1) % 16)
    if cycle_pos in [0, 1]:
        return "None"
    elif cycle_pos in [2, 3]:
        return "NS"
    elif cycle_pos in [4, 5]:
        return "EW"
    else:
        return "Both"

# Function to generate LIN viewer URL and fetch hands
def fetch_hands_from_lin(event_id, board_num):
    """Fetch hand distribution from BBO LIN viewer"""
    try:
        # BBO LIN URL pattern for vugraph boards
        lin_url = f"https://www.bridgebase.com/myhands/hands.php?id={event_id}&b={board_num}"
        
        response = requests.get(lin_url, timeout=5)
        response.raise_for_status()
        
        html = response.text
        
        # Look for hand pattern in the page
        # Pattern: "hand": "S.H.D.C ..."
        matches = re.findall(r'"hand"\s*:\s*"([^"]+)"', html)
        
        if matches:
            # Usually 4 matches for N, E, S, W
            if len(matches) >= 4:
                return {
                    'N': matches[0],
                    'E': matches[1],
                    'S': matches[2],
                    'W': matches[3]
                }
        
        print(f"    Could not find hands in LIN data")
        return None
        
    except Exception as e:
        print(f"    Error fetching LIN: {e}")
        return None

# Fetch missing hands
fetched_count = 0
failed_count = 0

for event_id in sorted(needed_boards.keys()):
    print(f"\nFetching Event {event_id}...")
    
    for board_num in sorted(needed_boards[event_id]):
        key = f"{event_id}_{board_num}"
        
        hands = fetch_hands_from_lin(event_id, board_num)
        
        if hands and all(h for h in hands.values()):
            hand_record = {
                'event': event_id,
                'board': board_num,
                'dealer': get_dealer(board_num),
                'date': '',  # Will fill from board results if available
                'hands': hands
            }
            
            hands_dict[key] = hand_record
            print(f"  Board {board_num}: OK")
            fetched_count += 1
        else:
            print(f"  Board {board_num}: FAILED")
            failed_count += 1
        
        sleep(0.5)  # Rate limiting

print(f"\n\nFetch Summary:")
print(f"  Successfully fetched: {fetched_count}")
print(f"  Failed: {failed_count}")
print(f"  Total in database now: {len(hands_dict)}")

# Save updated hands database
output = list(hands_dict.values())
with open(HANDS_DB_PATH, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\nSaved {len(output)} hands to {HANDS_DB_PATH}")
