#!/usr/bin/env python3
"""
Import DD values from Dealmaster results
After Dealmaster calculates DD, export the results and paste them here
"""

import json
import re

print("""
╔════════════════════════════════════════════════════════════════╗
║          DEALMASTER DD RESULTS IMPORT                          ║
║                                                                ║
║  After calculating in Dealmaster:                              ║
║  1. Export or copy the DD results                              ║
║  2. Paste them below (one board per line)                      ║
║  3. Format: Board#: NN=9 EN=4 SN=9 WN=4 (etc for all suits)   ║
║                                                                ║
║  Enter 'done' when finished, 'skip' to auto-generate           ║
╚════════════════════════════════════════════════════════════════╝
""")

dd_values = {}

while True:
    try:
        line = input("\nEnter DD result (or 'done'/'skip'): ").strip()
        
        if line.lower() == 'done':
            break
        elif line.lower() == 'skip':
            print("Skipping manual input...")
            break
        elif not line:
            continue
        
        # Try to parse the line
        # Expected format: "Board 1: NN=9 EN=4 SN=9 WN=4 NS=8 ES=5 SS=8 WS=5 NH=8 EH=5 SH=8 WH=5 ND=7 ED=6 SD=7 WD=6 NC=7 EC=6 SC=7 WC=6"
        
        match = re.match(r'[Bb]oard\s+(\d+):', line)
        if not match:
            print("  ✗ Invalid format - start with 'Board N:'")
            continue
        
        board_num = int(match.group(1))
        
        # Parse trick values
        # Suits: NT (no suit), S, H, D, C
        # Players: N, E, S, W
        
        tricks = {}
        for player in ['N', 'E', 'S', 'W']:
            tricks[player] = {}
            for suit in ['NT', 'S', 'H', 'D', 'C']:
                pattern = f'{player}{suit}=(\d+)'
                m = re.search(pattern, line)
                if m:
                    tricks[player][suit] = int(m.group(1))
        
        # Validate - check complementary sums
        valid = True
        for suit in ['NT', 'S', 'H', 'D', 'C']:
            ns_sum = tricks.get('N', {}).get(suit, 0) + tricks.get('S', {}).get(suit, 0)
            ew_sum = tricks.get('E', {}).get(suit, 0) + tricks.get('W', {}).get(suit, 0)
            if ns_sum != 13 or ew_sum != 13:
                print(f"  ✗ Invalid - {suit}: N+S={ns_sum}, E+W={ew_sum} (both should be 13)")
                valid = False
                break
        
        if valid and len(tricks) == 4:
            dd_values[board_num] = tricks
            print(f"  ✓ Board {board_num} accepted")
        else:
            print(f"  ✗ Missing or invalid values for Board {board_num}")
    
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        exit()

if dd_values:
    # Load database
    with open('app/www/hands_database.json', encoding='utf-8') as f:
        db = json.load(f)
    
    boards = db['events']['hosgoru_04_01_2026']['boards']
    
    # Update with DD values
    updated = 0
    for board_num, tricks in dd_values.items():
        if str(board_num) in boards:
            board = boards[str(board_num)]
            
            # Store as dict with suit keys
            board['dd_analysis'] = {
                'NT': {'N': tricks['N']['NT'], 'E': tricks['E']['NT'], 
                       'S': tricks['S']['NT'], 'W': tricks['W']['NT']},
                'S':  {'N': tricks['N']['S'],  'E': tricks['E']['S'],  
                       'S': tricks['S']['S'],  'W': tricks['W']['S']},
                'H':  {'N': tricks['N']['H'],  'E': tricks['E']['H'],  
                       'S': tricks['S']['H'],  'W': tricks['W']['H']},
                'D':  {'N': tricks['N']['D'],  'E': tricks['E']['D'],  
                       'S': tricks['S']['D'],  'W': tricks['W']['D']},
                'C':  {'N': tricks['N']['C'],  'E': tricks['E']['C'],  
                       'S': tricks['S']['C'],  'W': tricks['W']['C']}
            }
            updated += 1
    
    # Save
    with open('app/www/hands_database.json', 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Updated {updated} boards in database")
    print("  Refresh your browser to see the new DD values")
else:
    print("\nNo DD values entered.")
