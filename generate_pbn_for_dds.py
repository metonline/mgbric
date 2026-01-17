#!/usr/bin/env python3
"""
Generate PBN file for batch upload to DDS Bridge Solver.
1. Run this script to create hands_for_dds.pbn
2. Go to https://dds.bridgewebs.com/bsol_standalone/ddummy.html
3. Upload/paste the PBN file
4. Download the results as HTML
5. Save as dd_results.html in this folder
6. Run parse_dd_results.py to update database
"""

import json
from pathlib import Path


def create_pbn_file(database):
    """Create PBN format file from hands_database.json for DDS solver."""
    pbn_lines = []
    
    for board_id, board_data in sorted(database.items(), key=lambda x: int(x[0])):
        try:
            event = board_data.get('tournament', f'BRIC Tournament').replace('"', "'")
            dealer = board_data.get('dealer', 'N')
            vuln = board_data.get('vulnerability', 'None')
            
            # Map vulnerability to PBN format
            vuln_map = {'None': 'None', 'NS': 'NS', 'EW': 'EW', 'Both': 'All',
                       'N': 'NS', 'S': 'NS', 'E': 'EW', 'W': 'EW'}
            vuln_pbn = vuln_map.get(vuln, 'None')
            
            # Convert compact notation to PBN: 'SAT73HAQ6DKJ7CK83' -> 'AT73.AQ6.KJ7.K83'
            def parse_hand(hand_str):
                suits = {'S': '', 'H': '', 'D': '', 'C': ''}
                current_suit = None
                for char in hand_str:
                    if char in suits:
                        current_suit = char
                    elif current_suit:
                        suits[current_suit] += char
                return '.'.join([suits[s] for s in ['S', 'H', 'D', 'C']])
            
            n_pbn = parse_hand(board_data['N'])
            e_pbn = parse_hand(board_data['E'])
            s_pbn = parse_hand(board_data['S'])
            w_pbn = parse_hand(board_data['W'])
            
            deal_str = f"{dealer}:{n_pbn} {e_pbn} {s_pbn} {w_pbn}"
            
            # Create PBN record
            pbn_lines.append(f'[Event "{event}"]')
            pbn_lines.append(f'[Board "{board_id}"]')
            pbn_lines.append(f'[Dealer "{dealer}"]')
            pbn_lines.append(f'[Vulnerable "{vuln_pbn}"]')
            pbn_lines.append(f'[Deal "{deal_str}"]')
            pbn_lines.append('')  # Blank line between boards
        
        except Exception as e:
            print(f"Error converting board {board_id}: {e}")
    
    return '\n'.join(pbn_lines)


def main():
    db_path = Path('hands_database.json')
    
    if not db_path.exists():
        print("[ERROR] hands_database.json not found")
        return
    
    with open(db_path) as f:
        database = json.load(f)
    
    print(f"[OK] Loaded {len(database)} boards from {db_path}")
    print(f"[INFO] Generating PBN file for batch DDS upload...\n")
    
    # Create PBN file
    pbn_content = create_pbn_file(database)
    pbn_path = Path('hands_for_dds.pbn')
    
    with open(pbn_path, 'w', encoding='utf-8') as f:
        f.write(pbn_content)
    
    print(f"[OK] Created {pbn_path}")
    print(f"     Boards: {len(database)}")
    print(f"     Size: {len(pbn_content):,} bytes")
    print(f"\n{'='*70}")
    print(f"INSTRUCTIONS - Get Exact DD Values from DDS Solver:")
    print(f"{'='*70}")
    print(f"\n1. Open DDS Bridge Solver:")
    print(f"   https://dds.bridgewebs.com/bsol_standalone/ddummy.html")
    print(f"\n2. Click 'Upload PBN' button")
    print(f"\n3. Select {pbn_path} file")
    print(f"\n4. Click 'Solve All' (or equivalent)")
    print(f"\n5. Wait for all {len(database)} boards to be solved")
    print(f"\n6. Right-click page -> 'Save as' -> hands_dd_results.html")
    print(f"\n7. Run: python parse_dd_results.py")
    print(f"   (this will extract DD values and update database)")
    print(f"\n{'='*70}")
    print(f"\nAlternative (Manual):")
    print(f"- Open {pbn_path} in a text editor")
    print(f"- Copy all content")
    print(f"- Paste into DDS solver's PBN input area")
    print(f"- Click Solve")


if __name__ == '__main__':
    main()
