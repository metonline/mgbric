#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch hands from Vugraph board summary pages for all 30 boards
Event 404377
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time

def fetch_board_hands(event_id, board_num):
    """Fetch hands for a single board"""
    url = f"https://clubs.vugraph.com/hosgoru/boardsummary.php?event={event_id}&board={board_num}"
    
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get all text content
        text = soup.get_text()
        
        # Check if page exists (not 404)
        if '404' in text[:500] or 'Not Found' in text[:500]:
            return None
        
        # Extract dealer
        dealer_match = re.search(r'Dealer\s*:?\s*([NESW])', text, re.IGNORECASE)
        dealer = dealer_match.group(1).upper() if dealer_match else 'N'
        
        # Extract vulnerability
        vuln_patterns = [
            r'Vuln\s*:?\s*([^:,\n]+)',
            r'Vulnerability\s*:?\s*([^:,\n]+)',
            r'V[uú]ln[.]?\s*:?\s*([^:,\n]+)'
        ]
        vulnerability = 'None'
        for pattern in vuln_patterns:
            vuln_match = re.search(pattern, text, re.IGNORECASE)
            if vuln_match:
                vuln_text = vuln_match.group(1).strip()
                # Normalize
                if 'NS' in vuln_text or 'N-S' in vuln_text:
                    vulnerability = 'N-S'
                elif 'EW' in vuln_text or 'E-W' in vuln_text:
                    vulnerability = 'E-W'
                elif 'None' in vuln_text or 'Hiçbir' in vuln_text:
                    vulnerability = 'None'
                elif 'Both' in vuln_text or 'All' in vuln_text:
                    vulnerability = 'Both'
                break
        
        # Extract hands - look for hand patterns
        # Patterns: N:SAKQ9... or SAKQ9H...
        hands = {
            'North': {'S': '', 'H': '', 'D': '', 'C': ''},
            'South': {'S': '', 'H': '', 'D': '', 'C': ''},
            'East': {'S': '', 'H': '', 'D': '', 'C': ''},
            'West': {'S': '', 'H': '', 'D': '', 'C': ''}
        }
        
        # Try to find hand strings for each player
        # Look for patterns like "North: SAKJ9..." or similar
        
        # Split text by player names
        for player in ['North', 'South', 'East', 'West']:
            # Look for player name followed by hand
            pattern = f'{player}[\\s:]*([A-Z]*[SHDC][A-Z0-9]*(?:[SHDC][A-Z0-9]*)*)'
            matches = re.findall(pattern, text, re.IGNORECASE)
            
            if matches:
                hand_str = matches[0]
                # Parse the hand string
                current_suit = None
                for char in hand_str:
                    if char in 'SHDC':
                        current_suit = char
                    elif current_suit and char in 'AKQJT23456789':
                        hands[player][current_suit] += char
        
        return {
            'board_num': board_num,
            'dealer': dealer,
            'vulnerability': vulnerability,
            'hands': hands
        }
    
    except Exception as e:
        print(f"  Error: {e}")
        return None

# Fetch all boards
event_id = 404377
print("="*70)
print("FETCHING ALL BOARD HANDS FROM VUGRAPH")
print("="*70)

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

for board_num in range(1, 31):
    print(f"Board {board_num}...", end=" ", flush=True)
    board_data = fetch_board_hands(event_id, board_num)
    
    if board_data:
        print(f"✅ {board_data['dealer']} dealer, {board_data['vulnerability']}")
        
        database["events"]["hosgoru_04_01_2026"]["boards"][str(board_num)] = {
            "dealer": board_data['dealer'],
            "vulnerability": board_data['vulnerability'],
            "hands": board_data['hands'],
            "dd_analysis": {},
            "results": [],
            "doubleVDummy": {
                "table": {},
                "par": "TBD",
                "date_generated": "2026-01-06"
            }
        }
    else:
        print("⚠️ Failed")
    
    time.sleep(0.5)  # Rate limiting

# Save database
output_file = 'app/www/hands_database.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(database, f, ensure_ascii=False, indent=2)

print("\n" + "="*70)
print(f"✅ Saved to: {output_file}")
print("="*70)

# Verify
with open(output_file, 'r', encoding='utf-8') as f:
    db_check = json.load(f)

print(f"\n✅ Total boards saved: {len(db_check['events']['hosgoru_04_01_2026']['boards'])}")

# Sample check
for board_num in [1, 2, 3]:
    b = db_check['events']['hosgoru_04_01_2026']['boards'][str(board_num)]
    print(f"\nBoard {board_num}: {b['dealer']} dealer, {b['vulnerability']}")
    for player in ['North', 'South', 'East', 'West']:
        hand = b['hands'][player]
        total_cards = sum(len(hand.get(s, '')) for s in ['S', 'H', 'D', 'C'])
        suits = ' '.join([f'{s}{hand[s]}' for s in ['S', 'H', 'D', 'C']])
        print(f"  {player:6}: {suits} ({total_cards} cards)")
