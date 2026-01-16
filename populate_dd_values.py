#!/usr/bin/env python3
"""
Batch populate DD (Double Dummy) values for all 30 boards.

This script helps you fill in DD contract levels for all boards.
For each board, it:
1. Generates a BBO link
2. Opens it in your browser
3. Waits for you to enter the DD values from BBO
4. Saves to the database

DD Values format:
- 0 = Pass (no contract possible)
- 1 = 1-level contract (7 tricks)
- 2 = 2-level contract (8 tricks)
- 3 = 3-level contract (9 tricks)
... up to 7 = 7-level contract (13 tricks)

Each board has 20 DD values (5 suits × 4 players)
"""

import json
import webbrowser
import time
import os
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / "app" / "www" / "hands_database.json"

def load_database():
    """Load the hands database."""
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_database(data):
    """Save the hands database."""
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def hand_to_lin(board_data):
    """Convert hand data to BBO LIN format."""
    hands = board_data.get('hands', {})
    
    def format_hand(player_hand):
        if not player_hand:
            return 'SDHC'
        suits = ['S', 'H', 'D', 'C']
        return ''.join(s + (player_hand.get(s, '-') or '-') for s in suits)
    
    n_hand = format_hand(hands.get('North'))
    s_hand = format_hand(hands.get('South'))
    e_hand = format_hand(hands.get('East'))
    w_hand = format_hand(hands.get('West'))
    
    dealer_pos = board_data.get('dealer', 'N').lower()
    md_string = f"{dealer_pos}{s_hand},{w_hand},{n_hand},{e_hand}"
    
    vuln_map = {'None': 'n', 'E': 'e', 'Both': 'b', 'W': 'o'}
    sv_string = vuln_map.get(board_data.get('vulnerability'), 'n')
    
    lin_string = f"md|{md_string}|sv|{sv_string}"
    return lin_string

def get_dd_values_from_user():
    """Get DD values from user input."""
    suits = ['NT', 'S', 'H', 'D', 'C']
    players = ['N', 'S', 'E', 'W']
    dd_analysis = {}
    
    print("\n" + "="*60)
    print("Enter DD CONTRACT LEVELS (0-7) for each suit/player")
    print("="*60)
    print("\nFormat: For each suit, enter 4 numbers (N, S, E, W)")
    print("Example: 0 0 3 3  (means N=pass, S=pass, E=3-level, W=3-level)")
    print("\n")
    
    for suit in suits:
        while True:
            try:
                input_str = input(f"  {suit:2s}: ").strip()
                if not input_str:
                    print("    Please enter 4 values")
                    continue
                
                values = [int(x) for x in input_str.split()]
                if len(values) != 4:
                    print(f"    Expected 4 values, got {len(values)}")
                    continue
                
                if any(v < 0 or v > 7 for v in values):
                    print("    Values must be 0-7")
                    continue
                
                for player, value in zip(players, values):
                    dd_analysis[f"{suit}{player}"] = value
                break
            except ValueError:
                print("    Please enter 4 numbers separated by spaces")
    
    return dd_analysis

def display_dd_summary(dd_analysis):
    """Display a summary of entered DD values."""
    suits = ['NT', 'S', 'H', 'D', 'C']
    players = ['N', 'S', 'E', 'W']
    
    print("\n" + "="*60)
    print("DD VALUES SUMMARY")
    print("="*60)
    print(f"{'Suit':<6} {'North':<8} {'South':<8} {'East':<8} {'West':<8}")
    print("-"*60)
    
    for suit in suits:
        values = [str(dd_analysis.get(f"{suit}{p}", "?")) for p in players]
        print(f"{suit:<6} {values[0]:<8} {values[1]:<8} {values[2]:<8} {values[3]:<8}")
    
    print("="*60)

def process_board(board_num, board_data):
    """Process a single board."""
    print(f"\n\n{'='*70}")
    print(f"BOARD {board_num}")
    print(f"{'='*70}")
    
    dealer = board_data.get('dealer', 'N')
    vuln = board_data.get('vulnerability', 'None')
    print(f"Dealer: {dealer}  |  Vulnerability: {vuln}")
    
    # Show current hands
    hands = board_data.get('hands', {})
    print(f"\nHands:")
    for player in ['North', 'South', 'East', 'West']:
        hand = hands.get(player, {})
        if hand:
            print(f"  {player}: ♠{hand.get('S', '-')} ♥{hand.get('H', '-')} ♦{hand.get('D', '-')} ♣{hand.get('C', '-')}")
    
    # Check if already has COMPLETE DD values (all 20 non-zero or deliberately set)
    existing_dd = board_data.get('dd_analysis', {})
    if existing_dd:
        total_values = len(existing_dd)
        non_zero_values = sum(1 for v in existing_dd.values() if v != 0)
        print(f"\nCurrent DD status: {non_zero_values}/{total_values} values set")
        
        # If all 20 values are present and not all zeros, consider it complete
        if total_values == 20 and non_zero_values >= 5:  # At least some values
            print(f"✓ DD values already exist for this board")
            print(f"  Skipping...")
            return False
    
    # Generate BBO link
    lin = hand_to_lin(board_data)
    bbo_url = f"https://www.bridgebase.com/tools/handviewer.html?lin={lin}"
    
    print(f"\nOpening BBO viewer...")
    print(f"URL: {bbo_url}")
    
    # Open in browser
    try:
        webbrowser.open(bbo_url)
        print("✓ Browser opened")
    except Exception as e:
        print(f"✗ Could not open browser: {e}")
        print(f"  Please open this URL manually: {bbo_url}")
    
    time.sleep(2)
    
    # Get DD values from user
    dd_values = get_dd_values_from_user()
    display_dd_summary(dd_values)
    
    # Confirm before saving
    while True:
        confirm = input("\nSave these values? (y/n): ").strip().lower()
        if confirm in ['y', 'yes']:
            return dd_values
        elif confirm in ['n', 'no']:
            print("Skipped - values not saved")
            return False
        else:
            print("Please enter 'y' or 'n'")

def main():
    """Main function."""
    print("\n" + "="*70)
    print("BRIDGE DD VALUE BATCH POPULATOR")
    print("="*70)
    print("\nThis script will help you populate DD values for all 30 boards.")
    print("For each board, you'll enter the contract levels from BBO.\n")
    
    # Load database
    try:
        data = load_database()
    except Exception as e:
        print(f"Error loading database: {e}")
        return
    
    # Get boards
    event = data.get('events', {}).get('hosgoru_04_01_2026', {})
    boards = event.get('boards', {})
    
    if not boards:
        print("No boards found in database")
        return
    
    # Sort board numbers
    board_nums = sorted([int(k) for k in boards.keys()])
    
    print(f"Found {len(board_nums)} boards: {board_nums}\n")
    
    # Process boards
    updated_count = 0
    skipped_count = 0
    
    for board_num in board_nums:
        board_data = boards[str(board_num)]
        
        result = process_board(board_num, board_data)
        
        if result:  # False means skipped, dict means updated
            board_data['dd_analysis'] = result
            updated_count += 1
            print(f"\n✓ Board {board_num} updated")
        else:
            skipped_count += 1
        
        # Ask to continue
        if board_num < board_nums[-1]:
            while True:
                cont = input(f"\nContinue to next board? (y/n/q): ").strip().lower()
                if cont in ['y', 'yes']:
                    break
                elif cont in ['n', 'no']:
                    print("Stopping...")
                    break
                elif cont in ['q', 'quit']:
                    print("Quitting without saving remaining boards")
                    save_database(data)
                    return
                else:
                    print("Please enter 'y', 'n', or 'q'")
            
            if cont in ['n', 'no']:
                break
    
    # Save database
    print(f"\n\n{'='*70}")
    print("SAVING DATABASE...")
    try:
        save_database(data)
        print(f"✓ Database saved!")
        print(f"\nSummary:")
        print(f"  Boards updated: {updated_count}")
        print(f"  Boards skipped: {skipped_count}")
        print(f"  Total: {updated_count + skipped_count}")
    except Exception as e:
        print(f"✗ Error saving database: {e}")

if __name__ == '__main__':
    main()
