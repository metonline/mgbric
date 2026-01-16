#!/usr/bin/env python3
"""
Import DD data for all 30 boards at once
Paste the complete data (all 30 boards) and this script will import it all
"""

import json
import re

print("""
╔════════════════════════════════════════════════════════════════╗
║          BATCH DD IMPORT - ALL 30 BOARDS                       ║
║                                                                ║
║  Paste all 30 boards' DD data in this format:                  ║
║                                                                ║
║  Board 1: S_N=2 S_S=2 S_E=11 S_W=11 D_N=9 D_E=4 D_S=9 D_W=4   ║
║           H_N=11 H_E=2 H_S=11 H_W=2 C_N=9 C_E=4 C_S=9 C_W=4   ║
║           NT_N=10 NT_E=3 NT_S=10 NT_W=3                        ║
║  Board 2: ...                                                   ║
║  ...                                                            ║
║  Board 30: ...                                                  ║
║                                                                ║
║  Or simpler - just 20 values per line in order:                ║
║  Board 1: 2 2 11 11 9 4 9 4 11 2 11 2 9 4 9 4 10 3 10 3       ║
║           (S: N S E W | D: N S E W | H: N S E W |             ║
║            C: N S E W | NT: N S E W)                           ║
║                                                                ║
║  Type or paste the data, then 'done' when finished:            ║
╚════════════════════════════════════════════════════════════════╝
""")

data_lines = []
print("\nEnter data (type 'done' when finished):\n")

while True:
    try:
        line = input()
        if line.lower().strip() == 'done':
            break
        if line.strip():
            data_lines.append(line)
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        exit()

if not data_lines:
    print("No data entered.")
    exit()

dd_values = {}

for line in data_lines:
    line = line.strip()
    if not line or line.startswith('#'):
        continue
    
    # Parse board number
    match = re.match(r'[Bb]oard\s+(\d+):\s*(.*)', line)
    if not match:
        print(f"✗ Invalid format: {line[:50]}")
        continue
    
    board_num = int(match.group(1))
    data_str = match.group(2)
    
    try:
        # Try parsing with suit labels: S_N=2 S_S=2 ...
        tricks = {'N': {}, 'E': {}, 'S': {}, 'W': {}}
        
        # Look for labeled format
        if '=' in data_str:
            for pattern_match in re.finditer(r'(\w+)_(\w)=(\d+)', data_str):
                suit = pattern_match.group(1)  # S, D, H, C, NT
                player = pattern_match.group(2)  # N, E, S, W
                value = int(pattern_match.group(3))
                
                if suit not in tricks:
                    tricks[suit] = {}
                tricks[suit][player] = value
        else:
            # Try simple format: 20 space-separated numbers
            # Order: S(4) D(4) H(4) C(4) NT(4)
            values = list(map(int, data_str.split()))
            if len(values) >= 20:
                idx = 0
                for suit in ['S', 'D', 'H', 'C', 'NT']:
                    for player in ['N', 'S', 'E', 'W']:
                        if suit not in tricks:
                            tricks[suit] = {}
                        tricks[suit][player] = values[idx]
                        idx += 1
        
        # Convert to our format and validate
        result = {}
        for player in ['N', 'E', 'S', 'W']:
            result[player] = {}
            for suit in ['NT', 'S', 'H', 'D', 'C']:
                if suit in tricks and player in tricks[suit]:
                    result[player][suit] = tricks[suit][player]
        
        # Validate complementary sums
        valid = True
        for suit in ['NT', 'S', 'H', 'D', 'C']:
            if all(suit in result[p] for p in ['N', 'E', 'S', 'W']):
                ns_sum = result['N'][suit] + result['S'][suit]
                ew_sum = result['E'][suit] + result['W'][suit]
                if ns_sum != 13 or ew_sum != 13:
                    print(f"Board {board_num}: ✗ Invalid {suit} (N+S={ns_sum}, E+W={ew_sum})")
                    valid = False
                    break
        
        if valid:
            # Convert to flat format for HTML: {NTN: 10, NTS: 10, SN: 2, ...}
            flat = {}
            for suit in ['NT', 'S', 'H', 'D', 'C']:
                for player in ['N', 'S', 'E', 'W']:
                    if suit in result[player]:
                        key = f"{suit}{player}"
                        flat[key] = result[player][suit]
            
            dd_values[board_num] = flat
            print(f"Board {board_num}: ✓")
        else:
            print(f"  (Skipping Board {board_num})")
    
    except Exception as e:
        print(f"Board {board_num}: ✗ Parse error - {str(e)[:40]}")

if not dd_values:
    print("\n✗ No valid boards parsed.")
    exit()

print(f"\n{'='*60}")
print(f"Parsed {len(dd_values)} boards successfully")
print(f"{'='*60}\n")

# Load database
with open('app/www/hands_database.json', encoding='utf-8') as f:
    db = json.load(f)

boards = db['events']['hosgoru_04_01_2026']['boards']

# Update
updated = 0
for board_num, tricks_flat in dd_values.items():
    if str(board_num) in boards:
        board = boards[str(board_num)]
        board['dd_analysis'] = tricks_flat
        updated += 1

# Save
with open('app/www/hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print(f"✓ Updated {updated} boards in database")
print("  Refresh your browser to see the new DD values!")
