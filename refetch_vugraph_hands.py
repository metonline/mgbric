#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Refetch hands from Vugraph for event 404377 (PAZAR SİMULTANE 04-01-2026)
"""

import requests
from bs4 import BeautifulSoup
import json
import re

def parse_hand_string(hand_str):
    """Parse hand string"""
    if not hand_str or hand_str.strip() == '-':
        return {'S': '', 'H': '', 'D': '', 'C': ''}
    
    hand_str = hand_str.strip()
    result = {}
    
    # Handle continuous format: SAKQ9HT3DKT7CQJ2
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
    """Fetch single board details"""
    url = f"https://clubs.vugraph.com/hosgoru/boardsummary.php?event={event_id}&board={board_num}"
    
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find dealer and vulnerability
        dealer_match = re.search(r'Dealer\s*:\s*([NESW])', soup.text)
        dealer = dealer_match.group(1) if dealer_match else 'N'
        
        vuln_match = re.search(r'Vulnerability\s*:\s*([^<]+)', soup.text)
        vulnerability = vuln_match.group(1).strip() if vuln_match else 'None'
        
        # Map vulnerability
        vuln_map = {
            'None': 'None',
            'N-S': 'N-S',
            'E-W': 'E-W',
            'Both': 'Both',
            'All': 'Both',
            'NS': 'N-S',
            'EW': 'E-W'
        }
        vulnerability = vuln_map.get(vulnerability, vulnerability)
        
        # Find hands
        hands_text = soup.find_all(text=re.compile(r'^[SHDC]'))
        
        north_hand = {'S': '', 'H': '', 'D': '', 'C': ''}
        south_hand = {'S': '', 'H': '', 'D': '', 'C': ''}
        east_hand = {'S': '', 'H': '', 'D': '', 'C': ''}
        west_hand = {'S': '', 'H': '', 'D': '', 'C': ''}
        
        # Look for hand patterns in the HTML
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for i, row in enumerate(rows):
                cells = row.find_all('td')
                for j, cell in enumerate(cells):
                    text = cell.get_text().strip()
                    # Look for position indicators
                    if 'North' in text or 'N' in text:
                        # Try to extract North's hand
                        if j + 1 < len(cells):
                            hand_text = cells[j + 1].get_text().strip()
                            north_hand = parse_hand_string(hand_text)
                    elif 'South' in text or 'S' in text:
                        if j + 1 < len(cells):
                            hand_text = cells[j + 1].get_text().strip()
                            south_hand = parse_hand_string(hand_text)
                    elif 'East' in text or 'E' in text:
                        if j + 1 < len(cells):
                            hand_text = cells[j + 1].get_text().strip()
                            east_hand = parse_hand_string(hand_text)
                    elif 'West' in text or 'W' in text:
                        if j + 1 < len(cells):
                            hand_text = cells[j + 1].get_text().strip()
                            west_hand = parse_hand_string(hand_text)
        
        return {
            'board_num': board_num,
            'dealer': dealer,
            'vulnerability': vulnerability,
            'North': north_hand,
            'South': south_hand,
            'East': east_hand,
            'West': west_hand
        }
    except Exception as e:
        print(f"Error fetching board {board_num}: {e}")
        return None

# Fetch all 30 boards
print("="*70)
print("FETCHING HANDS FROM VUGRAPH - EVENT 404377")
print("="*70)

event_id = 404377
boards_data = []

for board_num in range(1, 31):
    print(f"Fetching Board {board_num}...", end=" ", flush=True)
    board_info = fetch_board(event_id, board_num)
    if board_info:
        boards_data.append(board_info)
        print(f"✅ {board_info['dealer']} dealer, {board_info['vulnerability']}")
    else:
        print("⚠️ Failed")

# Create database
database = {
    "events": {
        "hosgoru_04_01_2026": {
            "name": "Hoşgörü Pazar Simultane",
            "date": "04.01.2026",
            "location": "Istanbul",
            "section": "A",
            "boards": {}
        }
    }
}

for board in boards_data:
    board_num = board['board_num']
    database["events"]["hosgoru_04_01_2026"]["boards"][str(board_num)] = {
        "dealer": board['dealer'],
        "vulnerability": board['vulnerability'],
        "hands": {
            "North": board['North'],
            "South": board['South'],
            "East": board['East'],
            "West": board['West']
        },
        "dd_analysis": {},
        "results": [],
        "doubleVDummy": {
            "table": {},
            "par": "TBD",
            "date_generated": "2026-01-06"
        }
    }

# Save
output_file = 'app/www/hands_database.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(database, f, ensure_ascii=False, indent=2)

print("\n" + "="*70)
print(f"✅ Fetched {len(boards_data)} boards from Vugraph")
print(f"✅ Saved to: {output_file}")
print("="*70)

# Verify first board
if boards_data:
    b1 = boards_data[0]
    print(f"\n✅ Sample - Board {b1['board_num']}:")
    for player in ['North', 'South', 'East', 'West']:
        hand = b1[player]
        suits = ' '.join([f'{s}{hand[s]}' for s in ['S', 'H', 'D', 'C']])
        print(f"  {player:6}: {suits}")
