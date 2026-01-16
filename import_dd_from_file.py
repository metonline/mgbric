#!/usr/bin/env python3
"""
Import DD values from a CSV file
Create a CSV with DD values and this script will import them
"""

import json
import csv

print("""
╔════════════════════════════════════════════════════════════════╗
║          DD VALUES IMPORT FROM CSV                             ║
║                                                                ║
║  Create a CSV file with this format:                           ║
║                                                                ║
║  board,N_NT,N_S,N_H,N_D,N_C,E_NT,E_S,E_H,E_D,E_C,...         ║
║  1,9,8,9,8,7,4,5,4,5,6,...                                     ║
║                                                                ║
║  Or simpler text file format - one line per board:             ║
║  Board 1: N_NT=9 N_S=8 N_H=9 N_D=8 N_C=7 E_NT=4 ...          ║
║                                                                ║
║  Save to: dd_values.txt or dd_values.csv                       ║
╚════════════════════════════════════════════════════════════════╝
""")

csv_file = 'dd_values.csv'
txt_file = 'dd_values.txt'

# Try CSV first
try:
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        dd_values = {}
        for row in reader:
            board_num = int(row['board'])
            dd_values[board_num] = {
                'N': {'NT': int(row['N_NT']), 'S': int(row['N_S']), 'H': int(row['N_H']), 'D': int(row['N_D']), 'C': int(row['N_C'])},
                'E': {'NT': int(row['E_NT']), 'S': int(row['E_S']), 'H': int(row['E_H']), 'D': int(row['E_D']), 'C': int(row['E_C'])},
                'S': {'NT': int(row['S_NT']), 'S': int(row['S_S']), 'H': int(row['S_H']), 'D': int(row['S_D']), 'C': int(row['S_C'])},
                'W': {'NT': int(row['W_NT']), 'S': int(row['W_S']), 'H': int(row['W_H']), 'D': int(row['W_D']), 'C': int(row['W_C'])}
            }
        
        found_csv = True
        found_txt = False
except FileNotFoundError:
    found_csv = False
    dd_values = {}

# Try TXT if CSV not found
if not found_csv:
    try:
        import re
        with open(txt_file, 'r') as f:
            dd_values = {}
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Parse: Board 1: N_NT=9 N_S=8 ...
                match = re.match(r'[Bb]oard\s+(\d+):', line)
                if not match:
                    continue
                
                board_num = int(match.group(1))
                tricks = {}
                
                for player in ['N', 'E', 'S', 'W']:
                    tricks[player] = {}
                    for suit in ['NT', 'S', 'H', 'D', 'C']:
                        pattern = f'{player}_{suit}=(\d+)'
                        m = re.search(pattern, line)
                        if m:
                            tricks[player][suit] = int(m.group(1))
                
                dd_values[board_num] = tricks
        
        found_txt = len(dd_values) > 0
    except FileNotFoundError:
        found_txt = False

if found_csv:
    print(f"✓ Found {csv_file} with {len(dd_values)} boards")
elif found_txt:
    print(f"✓ Found {txt_file} with {len(dd_values)} boards")
else:
    print(f"✗ No dd_values.csv or dd_values.txt found")
    print("\nCreate one of these files first:")
    print("  dd_values.csv - CSV format (recommended)")
    print("  dd_values.txt - Text format (one board per line)")
    exit()

if dd_values:
    # Load database
    with open('app/www/hands_database.json', encoding='utf-8') as f:
        db = json.load(f)
    
    boards = db['events']['hosgoru_04_01_2026']['boards']
    
    # Validate and update
    updated = 0
    errors = 0
    
    for board_num, tricks in dd_values.items():
        try:
            if str(board_num) not in boards:
                print(f"Board {board_num}: ✗ Not found in database")
                errors += 1
                continue
            
            # Validate complementary sums
            for suit in ['NT', 'S', 'H', 'D', 'C']:
                ns_sum = tricks['N'][suit] + tricks['S'][suit]
                ew_sum = tricks['E'][suit] + tricks['W'][suit]
                if ns_sum != 13 or ew_sum != 13:
                    print(f"Board {board_num}: ✗ Invalid {suit} (N+S={ns_sum}, E+W={ew_sum})")
                    errors += 1
                    break
            else:
                # Update database
                board = boards[str(board_num)]
                board['dd_analysis'] = {
                    'NT': {'N': tricks['N']['NT'], 'E': tricks['E']['NT'], 'S': tricks['S']['NT'], 'W': tricks['W']['NT']},
                    'S':  {'N': tricks['N']['S'],  'E': tricks['E']['S'],  'S': tricks['S']['S'],  'W': tricks['W']['S']},
                    'H':  {'N': tricks['N']['H'],  'E': tricks['E']['H'],  'S': tricks['S']['H'],  'W': tricks['W']['H']},
                    'D':  {'N': tricks['N']['D'],  'E': tricks['E']['D'],  'S': tricks['S']['D'],  'W': tricks['W']['D']},
                    'C':  {'N': tricks['N']['C'],  'E': tricks['E']['C'],  'S': tricks['S']['C'],  'W': tricks['W']['C']}
                }
                updated += 1
                print(f"Board {board_num}: ✓")
        except (KeyError, TypeError) as e:
            print(f"Board {board_num}: ✗ Error - {str(e)}")
            errors += 1
    
    if updated > 0:
        # Save
        with open('app/www/hands_database.json', 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ Successfully updated {updated} boards")
        print("  Refresh your browser to see new DD values")
    
    if errors > 0:
        print(f"✗ {errors} errors found")
