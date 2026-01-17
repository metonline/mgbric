#!/usr/bin/env python3
"""
Fetch EXACT Double Dummy (DD) values using system Python's DDS library.
This script runs in system Python (which has dds module installed).
"""

import json
from pathlib import Path
import dds

def parse_hand(hand_str):
    """Parse 'SAT73HAQ6DKJ7CK83' format to PBN."""
    suits = {'S': '', 'H': '', 'D': '', 'C': ''}
    current_suit = None
    
    for char in hand_str:
        if char in suits:
            current_suit = char
        elif current_suit:
            suits[current_suit] += char
    
    return '.'.join([suits[s] for s in ['S', 'H', 'D', 'C']])


def solve_board(N, S, E, W, dealer='N', vulnerability='None'):
    """Solve board using DDS library."""
    try:
        # Convert to PBN format
        n_pbn = parse_hand(N)
        s_pbn = parse_hand(S)
        e_pbn = parse_hand(E)
        w_pbn = parse_hand(W)
        
        # Create deal string for dds: "N:N_hand E_hand S_hand W_hand vuln"
        # Vulnerability: 0=None, 1=NS, 2=EW, 3=Both
        vuln_map = {'None': 0, 'NS': 1, 'EW': 2, 'Both': 3, 'N': 1, 'S': 1, 'E': 2, 'W': 2}
        vuln_code = vuln_map.get(vulnerability, 0)
        
        # Create deal dict
        deal = {
            'dealer': dealer,
            'vulnerable': vuln_code,
            'N': n_pbn,
            'E': e_pbn,
            'S': s_pbn,
            'W': w_pbn
        }
        
        # Solve all suits
        results = {}
        suit_names = ['NT', 'S', 'H', 'D', 'C']
        player_names = ['N', 'E', 'S', 'W']
        
        for suit_idx, suit_name in enumerate(suit_names):
            # dds.calc_all_tables or similar
            # Let's try the calc_dd_table function
            trump_code = {0: 4, 1: 0, 2: 1, 3: 2, 4: 3}[suit_idx]  # NT=4, S=0, H=1, D=2, C=3
            
            try:
                tricks = dds.calc_dd_table(deal, trump_code)
                if tricks and len(tricks) == 4:
                    for p_idx, p_name in enumerate(player_names):
                        results[f'{suit_name}{p_name}'] = tricks[p_idx]
                else:
                    print(f"Bad tricks value for {suit_name}: {tricks}")
                    return {}
            except AttributeError:
                # Try alternative function name
                try:
                    tricks = dds.CalcAllTables(deal)
                    # Extract results for this suit
                    for p_idx, p_name in enumerate(player_names):
                        results[f'{suit_name}{p_name}'] = tricks[suit_idx][p_idx]
                except Exception as e2:
                    print(f"Neither calc_dd_table nor CalcAllTables worked: {e2}")
                    return {}
        
        return results
    
    except Exception as e:
        print(f"Error in solve_board: {e}")
        return {}


def main():
    # Load database
    db_path = Path('hands_database.json')
    with open(db_path) as f:
        database = json.load(f)
    
    print(f"[INFO] Loaded {len(database)} boards")
    print(f"[INFO] Computing EXACT DD values using pyDDS...\n")
    
    updated = 0
    errors = 0
    
    for board_id in sorted(database.keys(), key=int):
        board_data = database[board_id]
        try:
            N = board_data['N']
            S = board_data['S']
            E = board_data['E']
            W = board_data['W']
            dealer = board_data.get('dealer', 'N')
            vulnerability = board_data.get('vulnerability', 'None')
            
            dd_results = solve_board(N, S, E, W, dealer, vulnerability)
            
            if dd_results and len(dd_results) == 20:
                board_data['dd_analysis'] = dd_results
                updated += 1
                
                if updated % 10 == 0:
                    print(f"[OK] Board {board_id}: {len(dd_results)} contracts solved")
            else:
                errors += 1
                if errors <= 5:
                    print(f"[ERROR] Board {board_id}: Incomplete results ({len(dd_results)}/20)")
        
        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"[ERROR] Board {board_id}: {str(e)}")
    
    # Save
    with open(db_path, 'w') as f:
        json.dump(database, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"[DONE] Updated {updated}/{len(database)} boards with EXACT DD values")
    print(f"[SAVED] {db_path}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
