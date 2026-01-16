#!/usr/bin/env python3
"""
Compute Double Dummy tables for all 30 boards using endplay library.
Stores results in dd_tables.json for display in HTML.
"""

import json
import subprocess
import sys
from pathlib import Path

def install_package(package_name):
    """Install a pip package."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

def try_endplay():
    """Try using endplay library for DD calculations."""
    try:
        from endplay import Hand, Deal
        return True
    except ImportError:
        return False

def calculate_dd_with_endplay():
    """Use endplay library to calculate DD tables."""
    from endplay import Hand, Deal
    
    db_path = Path('c:/Users/metin/Desktop/BRIC/app/www/hands_database.json')
    
    with open(db_path, 'r') as f:
        database = json.load(f)
    
    dd_results = {}
    
    print("Computing DD tables using endplay library...")
    
    for board_num in range(1, 31):
        board_key = str(board_num)
        if board_key not in database:
            continue
        
        board_data = database[board_key]
        
        try:
            # Create Hand objects
            n_suit_str = f"{board_data['N'].get('S', '')}.{board_data['N'].get('H', '')}.{board_data['N'].get('D', '')}.{board_data['N'].get('C', '')}"
            s_suit_str = f"{board_data['S'].get('S', '')}.{board_data['S'].get('H', '')}.{board_data['S'].get('D', '')}.{board_data['S'].get('C', '')}"
            e_suit_str = f"{board_data['E'].get('S', '')}.{board_data['E'].get('H', '')}.{board_data['E'].get('D', '')}.{board_data['E'].get('C', '')}"
            w_suit_str = f"{board_data['W'].get('S', '')}.{board_data['W'].get('H', '')}.{board_data['W'].get('D', '')}.{board_data['W'].get('C', '')}"
            
            n_hand = Hand(n_suit_str)
            s_hand = Hand(s_suit_str)
            e_hand = Hand(e_suit_str)
            w_hand = Hand(w_suit_str)
            
            # Create deal
            deal = Deal(n=n_hand, e=e_hand, s=s_hand, w=w_hand)
            
            # Calculate tricks for each suit
            dd_table = []
            for suit in ['S', 'H', 'D', 'C', 'N']:
                tricks = deal.dd_table[suit]
                dd_table.append(tricks[0])  # NS tricks
            
            dd_results[board_key] = {
                'tricks': dd_table,
                'suits': ['S', 'H', 'D', 'C', 'NT'],
                'NS_tricks': dd_table,
                'EW_tricks': [13 - t for t in dd_table]
            }
            
            print(f"Board {board_num}: S={dd_table[0]} H={dd_table[1]} D={dd_table[2]} C={dd_table[3]} NT={dd_table[4]}")
            
        except Exception as e:
            print(f"Board {board_num}: Error - {e}")
    
    # Save DD tables
    output_path = Path('c:/Users/metin/Desktop/BRIC/app/www/dd_tables.json')
    with open(output_path, 'w') as f:
        json.dump(dd_results, f, indent=2)
    
    print(f"\n✅ DD tables saved to {output_path}")
    print(f"Total boards processed: {len(dd_results)}")

def main():
    # Check if endplay is installed
    if not try_endplay():
        print("Installing endplay library...")
        try:
            install_package("endplay")
            print("✅ endplay installed")
        except:
            print("❌ Could not install endplay, using basic computation...")
            return
    
    calculate_dd_with_endplay()

if __name__ == '__main__':
    main()
