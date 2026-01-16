#!/usr/bin/env python3
"""
Extract hands from LIN file and analyze with DD solver
"""
import re
import json
import requests
from urllib.parse import quote

def parse_lin_file(filepath):
    """Parse LIN file and extract board data"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all board records - each starts with qx|o[number]|
    # Format: md|[dealer][hands]...ah|Board [number]|
    
    boards = {}
    
    # Split by qx| to get individual records
    records = content.split('qx|')
    
    for record in records[1:]:  # Skip first empty split
        # Extract board number from ah|Board X|
        board_match = re.search(r'ah\|Board (\d+)\|', record)
        if not board_match:
            continue
        
        board_num = int(board_match.group(1))
        
        # Extract hands from md| section
        # Format: md|[dealer][N hand],[E hand],[S hand],[W hand],|
        md_match = re.search(r'md\|([a-z])([^|]+)\|', record)
        if not md_match:
            continue
        
        dealer = md_match.group(1).upper()
        hands_str = md_match.group(2)
        
        # Split into 4 hands
        hand_parts = hands_str.split(',')
        if len(hand_parts) < 4:
            print(f"Board {board_num}: Not enough hands")
            continue
        
        # Parse vulnerability from sv| section
        sv_match = re.search(r'sv\|([a-z])\|', record)
        vuln = 'None'
        if sv_match:
            vuln_code = sv_match.group(1)
            vuln_map = {'n': 'None', 'e': 'E', 'b': 'Both', 'o': 'None'}
            vuln = vuln_map.get(vuln_code, 'None')
        
        # Convert BBO hand format to suit-oriented
        def parse_bbo_hand(hand_str):
            """Parse BBO hand format: S27TH236D5689QC2T"""
            hand = {'S': '', 'H': '', 'D': '', 'C': ''}
            current_suit = 'S'
            for char in hand_str:
                if char in 'SHDC':
                    current_suit = char
                else:
                    hand[current_suit] += char
            return hand
        
        # Dealer is always first, then N, E, S in BBO
        # But in md| section: position depends on dealer
        # Standard: md|[dealer][N],[E],[S],[W]|
        
        dealers = hand_parts[0]
        n_hand = parse_bbo_hand(hand_parts[1]) if len(hand_parts) > 1 else {}
        e_hand = parse_bbo_hand(hand_parts[2]) if len(hand_parts) > 2 else {}
        s_hand = parse_bbo_hand(hand_parts[3]) if len(hand_parts) > 3 else {}
        w_hand = parse_bbo_hand(hand_parts[0][1:]) if len(hand_parts[0]) > 1 else {}
        
        boards[board_num] = {
            'dealer': dealer,
            'vulnerability': vuln,
            'north': n_hand,
            'east': e_hand,
            'south': s_hand,
            'west': w_hand,
            'raw': hands_str
        }
    
    return boards

def lin_to_pbn(board_num, dealer, vuln, hands):
    """Convert hand data to PBN format"""
    # PBN format example:
    # [Deal "N:♠QJ65.♥QT9.♦KJ8.♣AK2 ♠AT.♥AK.♦AT64.♣QJ963 ♠K9432.♥8765.♦Q9.♣87 ♠87.♥J432.♦7532.♣T54"]
    
    def format_hand(hand):
        suits = ['S', 'H', 'D', 'C']
        hand_str = ''
        for i, suit in enumerate(suits):
            cards = hand.get(suit, '')
            if not cards:
                cards = '-'
            hand_str += cards
            if i < 3:
                hand_str += '.'
        return hand_str
    
    dealer_map = {'N': 'N', 'E': 'E', 'S': 'S', 'W': 'W'}
    vuln_map = {
        'None': '-',
        'E': 'EW',
        'N': 'NS',
        'Both': 'All'
    }
    
    pbn = f"""[Event ""]
[Site ""]
[Date ""]
[Board "{board_num}"]
[West "{format_hand(hands.get('west', {}))}"]
[North "{format_hand(hands.get('north', {}))}"]
[East "{format_hand(hands.get('east', {}))}"]
[South "{format_hand(hands.get('south', {}))}"]
[Dealer "{dealer_map.get(dealer, 'N')}"]
[Vulnerable "{vuln_map.get(vuln, '-')}"]
[Deal "N:{format_hand(hands.get('north', {}))} E:{format_hand(hands.get('east', {}))} S:{format_hand(hands.get('south', {}))} W:{format_hand(hands.get('west', {}))}"]
"""
    return pbn

def main():
    lin_file = r"c:\Users\metin\Downloads\2026-01-04 23.12 #46747 Teams Untitled.lin"
    
    print("Parsing LIN file...")
    boards = parse_lin_file(lin_file)
    
    print(f"Found {len(boards)} boards")
    
    for board_num in sorted(boards.keys())[:5]:  # Show first 5
        board = boards[board_num]
        print(f"\nBoard {board_num}:")
        print(f"  Dealer: {board['dealer']}")
        print(f"  Vulnerability: {board['vulnerability']}")
        print(f"  North: {board['north']}")
        print(f"  East: {board['east']}")
        print(f"  South: {board['south']}")
        print(f"  West: {board['west']}")
        
        pbn = lin_to_pbn(board_num, board['dealer'], board['vulnerability'], board)
        print("PBN Preview:")
        print(pbn[:200])

if __name__ == '__main__':
    main()
