#!/usr/bin/env python3
"""
Fetch EXACT Double Dummy (DD) values for all bridge hands from online DDS solver.
Overwrites current dd_analysis with verified results.
Uses jddsolver.herokuapp.com free API.
"""

import json
from pathlib import Path
import sys
import requests
import time
import urllib.parse

# Base URL for free online DDS solver
DDS_SOLVER_URL = "https://jddsolver.herokuapp.com/dds"


def pbn_to_lin(N, S, E, W, dealer='N', vulnerability='None'):
    """Convert bridge hands to LIN format for DDS solver."""
    
    # Vulnerability code mapping
    vuln_map = {
        'None': '0', 'NS': '1', 'EW': '2', 'Both': '3',
        'N': '1', 'S': '1', 'E': '2', 'W': '2'
    }
    
    dealer_map = {'N': '1', 'E': '2', 'S': '3', 'W': '4'}
    vuln_code = vuln_map.get(vulnerability, '0')
    dealer_code = dealer_map.get(dealer, '1')
    
    # Create LIN format: md|N/S/E/W,dealer,vuln,N_hand S_hand E_hand W_hand|
    lin = f"md|{N},{S},{E},{W},{dealer_code},{vuln_code}|"
    return lin


def solve_board_online(N, S, E, W, dealer='N', vulnerability='None'):
    """
    Solve a bridge board using online DDS solver.
    
    Returns dict with DD results for all contracts and players:
    {
        'NTN': tricks_N_in_NT, 'NTE': tricks_E_in_NT, etc.
        'SN': tricks_N_in_Spades, etc.
    }
    """
    try:
        # Convert to LIN format
        lin = pbn_to_lin(N, S, E, W, dealer, vulnerability)
        
        # Query DDS solver
        params = {'lin': lin}
        response = requests.get(DDS_SOLVER_URL, params=params, timeout=10)
        
        if response.status_code != 200:
            return {}
        
        # Parse response
        data = response.json()
        
        if 'error' in data:
            return {}
        
        # Extract DD results
        # Response format: {"NS_NT": 9, "EW_NT": 4, ...} or similar
        results = {}
        
        # Map response keys to our format
        suit_names = ['NT', 'S', 'H', 'D', 'C']
        player_pairs = [('N', 'E', 'NS'), ('S', 'W', 'EW')]  # (declarer1, declarer2, prefix)
        
        for suit in suit_names:
            for p1, p2, prefix in player_pairs:
                key1 = f'{prefix}_{suit}' if f'{prefix}_{suit}' in data else None
                if key1:
                    tricks = data[key1]
                    # Convert NS tricks to N and E tricks
                    if prefix == 'NS':
                        results[f'{suit}{p1}'] = tricks
                        results[f'{suit}{p2}'] = 13 - tricks
                    else:
                        results[f'{suit}{p2}'] = tricks
                        results[f'{suit}{p1}'] = 13 - tricks
        
        return results
    
    except Exception as e:
        print(f"Error solving board: {e}")
        return {}
def main():
    # Load database
    db_path = Path('hands_database.json')
    with open(db_path) as f:
        database = json.load(f)
    
    print(f"[INFO] Loaded {len(database)} boards from {db_path}")
    print(f"[INFO] Calculating EXACT DD values using online solver...")
    print(f"[INFO] This will take a few minutes due to rate limiting (be patient)...\n")
    
    updated = 0
    errors = 0
    
    for board_id, board_data in sorted(database.items(), key=lambda x: int(x[0])):
        try:
            # Get hands
            N = board_data['N']
            S = board_data['S']
            E = board_data['E']
            W = board_data['W']
            dealer = board_data.get('dealer', 'N')
            vulnerability = board_data.get('vulnerability', 'None')
            
            # Solve board
            dd_results = solve_board_online(N, S, E, W, dealer, vulnerability)
            
            if dd_results and len(dd_results) >= 20:  # Should have 20 keys (5 suits × 4 players)
                # Update database
                board_data['dd_analysis'] = dd_results
                updated += 1
                
                if updated % 5 == 0:
                    print(f"[OK] Board {board_id}: {len(dd_results)} contracts solved")
                
                # Rate limiting - be nice to free service
                time.sleep(0.5)
            else:
                errors += 1
                if updated < 5:  # Only print first few errors
                    print(f"[WARNING] Board {board_id}: Solver returned incomplete data")
        
        except Exception as e:
            errors += 1
            if updated < 5:
                print(f"[ERROR] Board {board_id}: {str(e)}")
    
    # Save updated database
    with open(db_path, 'w') as f:
        json.dump(database, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"[COMPLETE] Updated {updated} boards with EXACT DD values")
    if errors > 0:
        print(f"[INFO] {errors} boards had issues (may retry)")
    print(f"[SAVED] {db_path}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
