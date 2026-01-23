#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validate ALL Event 405376 boards against vugraph source
Identifies all incorrect boards and outputs fixes needed
"""
import requests
from bs4 import BeautifulSoup
import re
import time

BASE_URL = "https://clubs.vugraph.com/hosgoru"
EVENT_ID = "405376"

# Map dealer numbers to positions
DEALER_MAP = {1: "N", 2: "E", 3: "S", 4: "W"}

def extract_hands_from_lin(lin_string):
    """Extract the 4 hands from a .lin md| string"""
    match = re.search(r'md\|(\d)(.+?)\|sv', lin_string)
    if not match:
        return None, None
    
    dealer_num = int(match.group(1))
    hands_str = match.group(2)
    hands = hands_str.split(',')
    
    if len(hands) != 3:
        return None, None
    
    return dealer_num, hands

def fetch_board_hands(board_num):
    """Fetch actual hands from vugraph for a board"""
    url = f"{BASE_URL}/boarddetails.php?event={EVENT_ID}&section=C&pair=43&direction=NS&board={board_num}"
    
    try:
        response = requests.get(url, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the bidding box section with hands
        hands = {}
        
        # Find player names and their hands
        text = soup.get_text()
        
        # Look for pattern: "NAME spades X hearts Y diamonds Z clubs W"
        pattern = r'([A-Z\s]+?)\s+spades\s+([A-Z0-9]+?)\s+hearts\s+([A-Z0-9]+?)\s+diamonds\s+([A-Z0-9]+?)\s+clubs\s+([A-Z0-9]+?)(?:\s|$)'
        
        matches = re.findall(pattern, text)
        
        for match in matches:
            name = match[0].strip()
            spades = match[1]
            hearts = match[2]
            diamonds = match[3]
            clubs = match[4]
            
            hand_str = f"{spades}.{hearts}.{diamonds}.{clubs}"
            
            # Determine position by name
            if 'KOPUZ' in name:
                hands['N'] = hand_str
            elif 'BAŞARAN' in name:
                hands['S'] = hand_str
            elif 'ATAV' in name or 'SEZAİ' in name:
                hands['E'] = hand_str
            elif 'BENGİSU' in name or 'FARUK' in name:
                hands['W'] = hand_str
        
        if len(hands) == 4:
            return hands
        else:
            print(f"  Board {board_num}: WARNING - Could not parse all hands from vugraph")
            return hands
            
    except Exception as e:
        print(f"  Board {board_num}: ERROR fetching - {e}")
        return {}

def rotate_hands_by_dealer(hand1, hand2, hand3, dealer_num):
    """
    Rotate hands to N-E-S-W based on dealer position
    For dealer=1 (N deals): hand1=N, hand2=E, hand3=S
    For dealer=2 (E deals): hand1=E, hand2=S, hand3=W
    For dealer=3 (S deals): hand1=S, hand2=W, hand3=N
    For dealer=4 (W deals): hand1=W, hand2=N, hand3=E
    """
    dealer_mapping = {
        1: {'hand1': 'N', 'hand2': 'E', 'hand3': 'S'},  # N deals
        2: {'hand1': 'E', 'hand2': 'S', 'hand3': 'W'},  # E deals
        3: {'hand1': 'S', 'hand2': 'W', 'hand3': 'N'},  # S deals
        4: {'hand1': 'W', 'hand2': 'N', 'hand3': 'E'},  # W deals
    }
    
    mapping = dealer_mapping[dealer_num]
    hands = {
        mapping['hand1']: hand1,
        mapping['hand2']: hand2,
        mapping['hand3']: hand3
    }
    return hands

print("="*70)
print("VALIDATING ALL EVENT 405376 BOARDS AGAINST VUGRAPH")
print("="*70)

# Read current .lin file
with open('event_405376.lin', 'r', encoding='utf-8') as f:
    lin_lines = f.readlines()

issues_found = []

for i, line in enumerate(lin_lines):
    if 'md|' not in line:
        continue
    
    board_match = re.search(r'ah\|Board (\d+)\|', line)
    if not board_match:
        continue
    
    board_num = int(board_match.group(1))
    
    # Extract hands from .lin
    dealer_num, lin_hands = extract_hands_from_lin(line)
    if dealer_num is None:
        print(f"\nBoard {board_num}: ERROR - Could not parse .lin file")
        continue
    
    dealer = DEALER_MAP[dealer_num]
    
    # Rotate .lin hands to N-E-S-W
    lin_rotated = rotate_hands_by_dealer(lin_hands[0], lin_hands[1], lin_hands[2], dealer_num)
    
    # Fetch actual hands from vugraph
    print(f"\nBoard {board_num}: Fetching from vugraph...", end='', flush=True)
    vugraph_hands = fetch_board_hands(board_num)
    
    if not vugraph_hands:
        print(" FAILED TO FETCH")
        continue
    
    print(" OK")
    
    # Compare
    all_match = True
    mismatches = []
    
    for pos in ['N', 'E', 'S', 'W']:
        lin_hand = lin_rotated.get(pos)
        vug_hand = vugraph_hands.get(pos)
        
        if lin_hand != vug_hand:
            all_match = False
            mismatches.append(f"    {pos}: LIN={lin_hand} vs VUGRAPH={vug_hand}")
    
    if all_match:
        print(f"  ✓ Board {board_num}: CORRECT")
    else:
        print(f"  ✗ Board {board_num}: INCORRECT")
        for mismatch in mismatches:
            print(mismatch)
        
        issues_found.append({
            'board': board_num,
            'line_idx': i,
            'dealer_num': dealer_num,
            'lin_hands': lin_hands,
            'correct_hands': vugraph_hands,
            'mismatches': mismatches
        })
    
    # Rate limit vugraph
    time.sleep(1)

print("\n" + "="*70)
print(f"SUMMARY: {len(issues_found)} boards with issues found")
print("="*70)

if issues_found:
    print("\nBOARDS TO FIX:")
    for issue in issues_found:
        board = issue['board']
        dealer = DEALER_MAP[issue['dealer_num']]
        print(f"\nBoard {board} (Dealer {dealer}):")
        for mismatch in issue['mismatches']:
            print(mismatch)

    # Output Python code to fix all boards
    print("\n" + "="*70)
    print("PYTHON CODE TO FIX ALL BOARDS:")
    print("="*70)
    print()
    print("# Add this to fix_all_boards.py")
    print("fixes = {")
    for issue in issues_found:
        board = issue['board']
        correct = issue['correct_hands']
        dealer_num = issue['dealer_num']
        
        # Find the correct order for this dealer
        if dealer_num == 1:  # N deals: N,E,S
            hand1, hand2, hand3 = correct['N'], correct['E'], correct['S']
        elif dealer_num == 2:  # E deals: E,S,W
            hand1, hand2, hand3 = correct['E'], correct['S'], correct['W']
        elif dealer_num == 3:  # S deals: S,W,N
            hand1, hand2, hand3 = correct['S'], correct['W'], correct['N']
        elif dealer_num == 4:  # W deals: W,N,E
            hand1, hand2, hand3 = correct['W'], correct['N'], correct['E']
        
        print(f'    {board}: "{hand1},{hand2},{hand3}",')
    print("}")
else:
    print("\n✓ ALL BOARDS ARE CORRECT!")
