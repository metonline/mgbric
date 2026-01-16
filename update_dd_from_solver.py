#!/usr/bin/env python3
"""
Update DD Analysis values in the database from DD solver results
Use this script to input DD values from the BridgeWebs solver

Example format:
Board 1: NN=9 EN=4 SN=9 WN=4 NS=8 ES=5 SS=8 WS=5 NH=8 EH=5 SH=8 WH=5 ND=7 ED=6 SD=7 WD=6 NC=7 EC=6 SC=7 WC=6
"""

import json
import sys

def parse_dd_input(line):
    """Parse a line of DD input"""
    # Format: Board 1: NN=9 EN=4 SN=9 WN=4 NS=8 ES=5 SS=8 WS=5 ...
    try:
        parts = line.strip().split(':')
        if len(parts) < 2:
            return None, None
        
        board_part = parts[0].replace('Board', '').strip()
        board_num = int(board_part)
        
        values_str = parts[1].strip()
        values = {}
        
        for pair in values_str.split():
            if '=' in pair:
                key, val = pair.split('=')
                values[key.strip()] = int(val.strip())
        
        return board_num, values
    except:
        return None, None

def update_database(dd_results):
    """Update the database with new DD values"""
    with open('app/www/hands_database.json', 'r', encoding='utf-8') as f:
        database = json.load(f)
    
    boards_data = database['events']['hosgoru_04_01_2026']['boards']
    updated_count = 0
    
    for board_num, dd_values in dd_results.items():
        board_key = str(board_num)
        if board_key in boards_data:
            boards_data[board_key]['dd_analysis'] = dd_values
            updated_count += 1
    
    # Save updated database
    with open('app/www/hands_database.json', 'w', encoding='utf-8') as f:
        json.dump(database, f, ensure_ascii=False, indent=2)
    
    return updated_count

print("=" * 80)
print("DD ANALYSIS UPDATER - Input DD solver results")
print("=" * 80)
print("\nINSTRUCTIONS:")
print("1. Go to: https://dds.bridgewebs.com/bsol_standalone/ddummy.htm")
print("2. Enter hands and get DD values")
print("3. Enter data in this format:")
print("   Board 1: NN=9 EN=4 SN=9 WN=4 NS=8 ES=5 SS=8 WS=5 NH=8 EH=5 SH=8 WH=5 ND=7 ED=6 SD=7 WD=6 NC=7 EC=6 SC=7 WC=6")
print("4. Type 'done' when finished")
print("=" * 80)
print()

dd_results = {}

while True:
    line = input("Enter DD results (or 'done'): ").strip()
    
    if line.lower() == 'done':
        break
    
    if not line:
        continue
    
    board_num, values = parse_dd_input(line)
    
    if board_num is None:
        print("❌ Invalid format. Use: Board X: KEY=VALUE KEY=VALUE ...")
        continue
    
    if not values:
        print("❌ No values found. Make sure format is: NN=9 EN=4 ...")
        continue
    
    dd_results[board_num] = values
    print(f"✓ Board {board_num}: {len(values)} values stored")

if dd_results:
    print(f"\n{'=' * 80}")
    print(f"Ready to update {len(dd_results)} boards")
    confirm = input("Continue with update? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        updated = update_database(dd_results)
        print(f"✓ Updated {updated} boards in hands_database.json")
        print("\nRefresh your browser to see the new DD values")
    else:
        print("❌ Update cancelled")
else:
    print("\nNo data entered")
