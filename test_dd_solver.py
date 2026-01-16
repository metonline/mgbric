#!/usr/bin/env python3
"""
Test DD Analysis values from the database against calculated DD values
using a DD solver
"""

import json
import sys

try:
    from dds import dds_bridge
    HAS_DDS = True
except ImportError:
    HAS_DDS = False
    print("dds module not found. Install with: pip install dds")
    
try:
    from pydds import DDSTable
    HAS_PYDDS = True
except ImportError:
    HAS_PYDDS = False

# Load the database
with open('app/www/hands_database.json', 'r', encoding='utf-8') as f:
    database = json.load(f)

# Get board 1 and board 2 for testing
boards_data = database['events']['hosgoru_04_01_2026']['boards']

def hand_to_pbn(hands):
    """Convert hand dictionary to PBN format"""
    n_spades = hands['North']['S']
    n_hearts = hands['North']['H']
    n_diamonds = hands['North']['D']
    n_clubs = hands['North']['C']
    
    s_spades = hands['South']['S']
    s_hearts = hands['South']['H']
    s_diamonds = hands['South']['D']
    s_clubs = hands['South']['C']
    
    e_spades = hands['East']['S']
    e_hearts = hands['East']['H']
    e_diamonds = hands['East']['D']
    e_clubs = hands['East']['C']
    
    w_spades = hands['West']['S']
    w_hearts = hands['West']['H']
    w_diamonds = hands['West']['D']
    w_clubs = hands['West']['C']
    
    # PBN format: N:S.H.D.C W.H.D.C E.H.D.C S.H.D.C
    pbn = f"N:{n_spades}.{n_hearts}.{n_diamonds}.{n_clubs} {w_spades}.{w_hearts}.{w_diamonds}.{w_clubs} {e_spades}.{e_hearts}.{e_diamonds}.{e_clubs} {s_spades}.{s_hearts}.{s_diamonds}.{s_clubs}"
    return pbn

print("=" * 70)
print("DD ANALYSIS VERIFICATION TEST")
print("=" * 70)

test_boards = [1, 2]

for board_num in test_boards:
    board_key = str(board_num)
    if board_key not in boards_data:
        print(f"\nBoard {board_num} not found")
        continue
    
    board_data = boards_data[board_key]
    hands = board_data['hands']
    current_dd = board_data.get('dd_analysis', {})
    
    print(f"\n{'='*70}")
    print(f"BOARD {board_num}")
    print(f"Dealer: {board_data['dealer']}, Vulnerability: {board_data['vulnerability']}")
    print(f"{'='*70}")
    
    # Display hands
    print(f"\nHands:")
    print(f"  North:  {hands['North']['S']} {hands['North']['H']} {hands['North']['D']} {hands['North']['C']}")
    print(f"  East:   {hands['East']['S']} {hands['East']['H']} {hands['East']['D']} {hands['East']['C']}")
    print(f"  South:  {hands['South']['S']} {hands['South']['H']} {hands['South']['D']} {hands['South']['C']}")
    print(f"  West:   {hands['West']['S']} {hands['West']['H']} {hands['West']['D']} {hands['West']['C']}")
    
    # Display current DD values from database
    print(f"\nCurrent DD Analysis in Database:")
    print(f"{'Suit':<6} {'N':<4} {'E':<4} {'S':<4} {'W':<4}")
    print("-" * 24)
    
    suits = ['NT', 'S', 'H', 'D', 'C']
    for suit in suits:
        n_tricks = current_dd.get(f'N{suit}', '?')
        e_tricks = current_dd.get(f'E{suit}', '?')
        s_tricks = current_dd.get(f'S{suit}', '?')
        w_tricks = current_dd.get(f'W{suit}', '?')
        print(f"{suit:<6} {n_tricks:<4} {e_tricks:<4} {s_tricks:<4} {w_tricks:<4}")
    
    if HAS_PYDDS:
        print(f"\n⚠️  To calculate correct DD values, install: pip install dds")
        print(f"Then run: python test_dd_solver.py")
    elif HAS_DDS:
        print(f"\nCalculating actual DD values with DDS...")
        try:
            pbn = hand_to_pbn(hands)
            print(f"\nPBN: {pbn}")
            
            # Use dds to calculate
            dd_table = dds_bridge(hands, tricks=True)
            
            print(f"\nCalculated DD Analysis (from DDS):")
            print(f"{'Suit':<6} {'N':<4} {'E':<4} {'S':<4} {'W':<4}")
            print("-" * 24)
            
            for suit in suits:
                print(f"{suit:<6} {dd_table[suit][0]:<4} {dd_table[suit][1]:<4} {dd_table[suit][2]:<4} {dd_table[suit][3]:<4}")
                
        except Exception as e:
            print(f"Error calculating DD: {e}")
    else:
        print(f"\n⚠️  No DD solver library found!")
        print(f"Install one of the following:")
        print(f"  - pip install dds")
        print(f"  - pip install pydds")

print(f"\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")
print("To calculate actual DD values and verify correctness:")
print("1. Install dds library: pip install dds")
print("2. Run this script again: python test_dd_solver.py")
print("\nIf your database DD values don't match calculated values,")
print("they need to be recalculated.")
