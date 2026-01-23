#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process Double Dummy (DD) Data for All Boards
Generate optimal scores and LOTT (Losers On Tricks) from correct hand data
Uses endplay library to calculate DD tables
"""

import json
import sys
from pathlib import Path
from datetime import datetime

try:
    from endplay.types import Deal, Player, Vul
    from endplay.dds import calc_dd_table, par
    ENDPLAY_AVAILABLE = True
except ImportError:
    print("ERROR: endplay library not found!")
    print("Install with: pip install endplay")
    ENDPLAY_AVAILABLE = False
    sys.exit(1)

HANDS_DB_PATH = Path(__file__).parent / "hands_database.json"
OUTPUT_PATH = Path(__file__).parent / "double_dummy" / "dd_results.json"

def hand_to_pbn(north, east, south, west, dealer='N'):
    """Convert hand format to PBN deal string"""
    if dealer == 'N':
        return f"N:{north} {east} {south} {west}"
    elif dealer == 'E':
        return f"E:{east} {south} {west} {north}"
    elif dealer == 'S':
        return f"S:{south} {west} {north} {east}"
    elif dealer == 'W':
        return f"W:{west} {north} {east} {south}"
    return f"N:{north} {east} {south} {west}"

def get_vul_enum(vuln_str):
    """Convert vulnerability string to Vul enum"""
    vuln_map = {
        'None': Vul.none,
        'NS': Vul.ns,
        'EW': Vul.ew,
        'Both': Vul.both,
        'All': Vul.both,
        'none': Vul.none,
        'ns': Vul.ns,
        'ew': Vul.ew,
        'both': Vul.both,
        'all': Vul.both,
        '-': Vul.none,
        'Yok': Vul.none,
    }
    return vuln_map.get(vuln_str, Vul.none)

def get_dealer_enum(dealer_str):
    """Convert dealer string to Player enum"""
    dealer_map = {
        'N': Player.north,
        'n': Player.north,
        'E': Player.east,
        'e': Player.east,
        'S': Player.south,
        's': Player.south,
        'W': Player.west,
        'w': Player.west,
    }
    return dealer_map.get(dealer_str, Player.north)

def parse_dd_table(table):
    """Convert endplay DD table to dict format"""
    result = {}
    
    # Convert table to string and parse
    table_str = str(table)
    parts = table_str.split(';')
    
    # Suit order from the string representation
    suits_order = ['C', 'D', 'H', 'S', 'NT']
    
    # Parse each player's results
    for part in parts[1:]:  # Skip first part (suit headers)
        if ':' in part:
            pos, values = part.split(':')
            tricks = values.split(',')
            result[pos] = {}
            for i, suit in enumerate(suits_order):
                if i < len(tricks):
                    result[pos][suit] = int(tricks[i].strip())
    
    return result

def calculate_dd_table(north, east, south, west, dealer='N', vuln='None'):
    """Calculate DD table for a deal"""
    try:
        # Create PBN string
        pbn_str = hand_to_pbn(north, east, south, west, dealer)
        
        # Create Deal object
        deal = Deal.from_pbn(pbn_str)
        deal.vul = get_vul_enum(vuln)
        
        # Calculate DD table
        dd_table = calc_dd_table(deal)
        
        # Parse the table to dict format
        result = parse_dd_table(dd_table)
        
        return result
    
    except Exception as e:
        import traceback
        print(f"    [DD Error: {str(e)[:80]}]", end='')
        return None

def main():
    print(f"\n{'='*70}")
    print(f"DOUBLE DUMMY DATA PROCESSING")
    print(f"Processing boards from hands_database.json")
    print(f"{'='*70}\n")
    
    # Load hands database
    try:
        with open(HANDS_DB_PATH, 'r', encoding='utf-8') as f:
            hands_data = json.load(f)
    except Exception as e:
        print(f"ERROR: Could not load {HANDS_DB_PATH}: {e}")
        return False
    
    print(f"Loaded {len(hands_data)} boards from hands_database.json\n")
    
    # Initialize output structure
    output_data = {
        'generated': datetime.now().isoformat(),
        'total_boards': len(hands_data),
        'boards': {}
    }
    
    # Process each board
    processed = 0
    failed = 0
    
    for i, board_data in enumerate(hands_data):
        board_num = board_data.get('board')
        event_id = '405376'  # All boards are from event 405376
        board_key = f"{event_id}_{board_num}"
        
        # Get hand data from 'hands' dict
        hands_dict = board_data.get('hands', {})
        north = hands_dict.get('N')
        east = hands_dict.get('E')
        south = hands_dict.get('S')
        west = hands_dict.get('W')
        
        if not all([north, east, south, west]):
            print(f"Board {board_key}: SKIP (missing hands)")
            failed += 1
            continue
        
        # Get dealer from board data
        dealer = board_data.get('dealer', 'N')
        
        # Get vulnerability (based on board number)
        # For standard EW/NS vulnerability tables
        board_mod = (board_num - 1) % 16
        if board_mod < 4:
            vuln = 'None'
        elif board_mod < 8:
            vuln = 'NS'
        elif board_mod < 12:
            vuln = 'EW'
        else:
            vuln = 'Both'
        
        print(f"Board {board_key}: ", end='', flush=True)
        
        # Calculate DD table
        dd_table = calculate_dd_table(north, east, south, west, dealer, vuln)
        
        if dd_table:
            output_data['boards'][board_key] = {
                'event': event_id,
                'board': board_num,
                'dealer': dealer,
                'vuln': vuln,
                'tricks': dd_table
            }
            print(f"OK")
            processed += 1
        else:
            print(f"FAILED")
            failed += 1
        
        if (i + 1) % 10 == 0:
            print(f"  Progress: {i+1}/{len(hands_data)}")
    
    # Save results
    print(f"\n" + "="*70)
    print(f"Saving results to {OUTPUT_PATH}...")
    
    try:
        with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"\nSUCCESS:")
        print(f"  Total processed: {processed}")
        print(f"  Failed: {failed}")
        print(f"  File: {OUTPUT_PATH}")
        print(f"{'='*70}\n")
        
        return True
    
    except Exception as e:
        print(f"ERROR saving file: {e}")
        return False

if __name__ == '__main__':
    if not ENDPLAY_AVAILABLE:
        print("ERROR: endplay library required")
        sys.exit(1)
    
    success = main()
    sys.exit(0 if success else 1)
