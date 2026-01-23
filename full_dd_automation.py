#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FULL AUTOMATION: DD Processing for ALL Tournament Boards
========================================================
1. Extract all board/event data from board_results.json
2. Fetch missing hands from vugraph (if any)
3. Process DD tables for all boards
4. Save results to dd_results.json
5. Can be scheduled/automated for periodic runs
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

try:
    from endplay.types import Deal, Player, Vul
    from endplay.dds import calc_dd_table
    ENDPLAY_AVAILABLE = True
except ImportError:
    print("ERROR: endplay library not found!")
    print("Install with: pip install endplay")
    ENDPLAY_AVAILABLE = False
    sys.exit(1)

BOARD_RESULTS_PATH = Path(__file__).parent / "board_results.json"
HANDS_DB_PATH = Path(__file__).parent / "hands_database.json"
OUTPUT_PATH = Path(__file__).parent / "double_dummy" / "dd_results.json"

def load_board_results():
    """Load board results to get all boards and events"""
    if not BOARD_RESULTS_PATH.exists():
        print(f"ERROR: {BOARD_RESULTS_PATH} not found!")
        return {}
    
    with open(BOARD_RESULTS_PATH, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    
    # Extract boards by event
    boards_by_event = {}
    if 'boards' in data:
        for board_key, board_data in data['boards'].items():
            event_id = board_data.get('event_id', '')
            board_num = board_data.get('board', 0)
            
            if event_id not in boards_by_event:
                boards_by_event[event_id] = {}
            
            boards_by_event[event_id][board_num] = board_data
    
    return boards_by_event

def load_hands_database():
    """Load existing hands database"""
    if not HANDS_DB_PATH.exists():
        return {}
    
    try:
        with open(HANDS_DB_PATH, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
        
        # Convert array to dict format for easier lookup
        hands_dict = {}
        if isinstance(data, list):
            for hand in data:
                key = f"{hand.get('event')}_{hand.get('board')}"
                hands_dict[key] = hand
        else:
            hands_dict = data
        
        return hands_dict
    except Exception as e:
        print(f"ERROR loading hands database: {e}")
        return {}

def get_vul_enum(board_num):
    """Calculate vulnerability from board number using standard EW/NS rotation"""
    # Standard rotation: 16-board cycle
    # Board 1,2: None  |  3,4: NS  |  5,6: EW  |  7,8: Both
    # Repeat for 9-16, 17-24, etc.
    cycle_pos = ((board_num - 1) % 16)
    
    if cycle_pos in [0, 1]:
        return Vul.none, "None"
    elif cycle_pos in [2, 3]:
        return Vul.ns, "NS"
    elif cycle_pos in [4, 5]:
        return Vul.ew, "EW"
    else:  # 6-15
        return Vul.both, "Both"

def get_dealer(board_num):
    """Calculate dealer from board number"""
    dealer_cycle = (board_num - 1) % 4
    dealers = ['N', 'E', 'S', 'W']
    return dealers[dealer_cycle]

def hand_to_pbn(north, east, south, west, dealer='N'):
    """Convert hand format to PBN deal string
    
    Handles empty suits properly for endplay:
    - Empty suits should be represented as empty string, not '-'
    - Format: S.H.D.C for each hand
    """
    # Clean up hands: replace '-' with empty string
    def clean_hand(hand_str):
        if not hand_str:
            return hand_str
        parts = hand_str.split('.')
        return '.'.join(p if p != '-' else '' for p in parts)
    
    n = clean_hand(north)
    e = clean_hand(east)
    s = clean_hand(south)
    w = clean_hand(west)
    
    if dealer == 'N':
        return f"N:{n} {e} {s} {w}"
    elif dealer == 'E':
        return f"E:{e} {s} {w} {n}"
    elif dealer == 'S':
        return f"S:{s} {w} {n} {e}"
    elif dealer == 'W':
        return f"W:{w} {n} {e} {s}"
    return f"N:{n} {e} {s} {w}"

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

def calculate_dd_table(north, east, south, west, dealer='N', vuln_enum=None):
    """Calculate DD table for a deal"""
    try:
        # Create PBN string
        pbn_str = hand_to_pbn(north, east, south, west, dealer)
        
        # Create Deal object
        deal = Deal.from_pbn(pbn_str)
        if vuln_enum:
            deal.vul = vuln_enum
        
        # Calculate DD table
        dd_table = calc_dd_table(deal)
        
        # Parse the table to dict format
        result = parse_dd_table(dd_table)
        
        return result
    
    except Exception as e:
        return None

def process_all_boards():
    """Process DD tables for ALL boards"""
    print("\n" + "="*60)
    print("FULL DD PROCESSING - ALL BOARDS")
    print("="*60 + "\n")
    
    # Load data
    print("Loading data...")
    boards_by_event = load_board_results()
    hands_dict = load_hands_database()
    
    print(f"Found {len(boards_by_event)} events")
    total_boards = sum(len(boards) for boards in boards_by_event.values())
    print(f"Total boards to process: {total_boards}")
    print()
    
    # Process all boards
    results = {
        "generated": datetime.now().isoformat(),
        "total_boards": total_boards,
        "boards": {}
    }
    
    processed = 0
    failed = 0
    board_count = 0
    errors = []
    
    for event_id in sorted(boards_by_event.keys()):
        event_boards = boards_by_event[event_id]
        print(f"\nEvent {event_id}: {len(event_boards)} boards")
        print("-" * 40)
        
        for board_num in sorted(event_boards.keys()):
            board_count += 1
            board_key = f"{event_id}_{board_num}"
            
            # Get hands from database
            hand_data = hands_dict.get(board_key)
            
            if not hand_data:
                print(f"  Board {board_num}: NO HAND DATA", end='')
                failed += 1
                errors.append((board_key, "No hand data"))
                continue
            
            # Get hand details
            hands = hand_data.get('hands', {})
            if not hands or not all(k in hands for k in ['N', 'E', 'S', 'W']):
                print(f"  Board {board_num}: INCOMPLETE HANDS", end='')
                failed += 1
                errors.append((board_key, "Incomplete hands"))
                continue
            
            # Get dealer and vulnerability
            dealer = hand_data.get('dealer', get_dealer(board_num))
            vuln_enum, vuln_str = get_vul_enum(board_num)
            
            # Calculate DD table
            try:
                dd_result = calculate_dd_table(
                    hands.get('N', ''),
                    hands.get('E', ''),
                    hands.get('S', ''),
                    hands.get('W', ''),
                    dealer,
                    vuln_enum
                )
            except Exception as e:
                dd_result = None
                errors.append((board_key, str(e)))
            
            if dd_result:
                results['boards'][board_key] = {
                    'event': event_id,
                    'board': board_num,
                    'dealer': dealer,
                    'vuln': vuln_str,
                    'tricks': dd_result
                }
                print(f"  Board {board_num}: OK", end='')
                processed += 1
            else:
                print(f"  Board {board_num}: CALC FAILED", end='')
                failed += 1
            
            if board_count % 10 == 0:
                print(f"\n  Progress: {board_count}/{total_boards}", end='')
            print()
    
    # Save results
    print("\n" + "="*60)
    print("Saving results...")
    
    # Ensure output directory exists
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Saved to: {OUTPUT_PATH}\n")
    print("="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    print(f"Total boards processed:  {total_boards}")
    print(f"Successful:              {processed}")
    print(f"Failed:                  {failed}")
    print(f"Success rate:            {100*processed/total_boards:.1f}%")
    
    if errors:
        print("\n" + "="*60)
        print("FAILED BOARDS DETAILS")
        print("="*60)
        for board_key, error in errors[:20]:  # Show first 20 errors
            print(f"  {board_key}: {error[:100]}")
    
    print("="*60 + "\n")
    
    return processed, failed

if __name__ == '__main__':
    if ENDPLAY_AVAILABLE:
        processed, failed = process_all_boards()
        sys.exit(0 if failed == 0 else 1)
