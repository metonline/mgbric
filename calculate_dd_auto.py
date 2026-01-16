#!/usr/bin/env python3
"""
Calculate DD (Double Dummy) contract levels for all 30 boards using dds library
"""
import json
import sys

try:
    import dds
except ImportError:
    print("Installing dds library...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "dds"])
    import dds

def hand_string_to_dds_format(hands_dict):
    """Convert hand dictionary to DDS format"""
    # DDS expects: 0=Spades, 1=Hearts, 2=Diamonds, 3=Clubs
    # Format: [S, H, D, C] as 4 strings
    return [
        hands_dict.get('S', ''),
        hands_dict.get('H', ''),
        hands_dict.get('D', ''),
        hands_dict.get('C', '')
    ]

def calculate_dd_for_hand(board_data):
    """Calculate DD values for a single hand"""
    try:
        hands = board_data['hands']
        
        # Convert to DDS format
        # DDS wants: North, East, South, West in that order
        # Each as a list [Spades, Hearts, Diamonds, Clubs] as strings
        
        north = hand_string_to_dds_format(hands['North'])
        east = hand_string_to_dds_format(hands['East'])
        south = hand_string_to_dds_format(hands['South'])
        west = hand_string_to_dds_format(hands['West'])
        
        # Map dealer to DDS format (0=N, 1=E, 2=S, 3=W)
        dealer_map = {'N': 0, 'E': 1, 'S': 2, 'W': 3}
        dealer = dealer_map.get(board_data.get('dealer', 'N'), 0)
        
        # Map vulnerability (0=None, 1=N-S, 2=E-W, 3=Both)
        vuln_map = {
            'None': 0,
            'N-S': 1,
            'E-W': 2,
            'Both': 3
        }
        vuln = vuln_map.get(board_data.get('vulnerability', 'None'), 0)
        
        # Create deal for DDS
        # Format: [N, E, S, W] where each is [S, H, D, C]
        deal = [north, east, south, west]
        
        # Calculate DD tricks
        # Returns: for each suit (NT, S, H, D, C) and each player (N, E, S, W)
        tricks = dds.calc_dd_table(deal, dealer, vuln)
        
        # tricks is a dict with keys like 'NT', 'S', 'H', 'D', 'C'
        # Each value is a dict with keys 'N', 'S', 'E', 'W' containing trick counts
        
        dd_analysis = {}
        
        for suit in ['NT', 'S', 'H', 'D', 'C']:
            if suit in tricks:
                suit_tricks = tricks[suit]
                for player in ['N', 'S', 'E', 'W']:
                    tricks_count = suit_tricks.get(player, 0)
                    # Convert tricks to contract level
                    contract_level = max(0, tricks_count - 6)  # 7 tricks = level 1
                    dd_analysis[f'{suit}{player}'] = contract_level
        
        return dd_analysis
        
    except Exception as e:
        print(f"Error calculating DD: {e}")
        return None

def main():
    db_file = r"c:\Users\metin\Desktop\BRIC\app\www\hands_database.json"
    
    print("Loading database...")
    with open(db_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    boards = data['events']['hosgoru_04_01_2026']['boards']
    
    print(f"Calculating DD for {len(boards)} boards...")
    
    updated_count = 0
    
    for board_num in sorted(boards.keys(), key=lambda x: int(x)):
        board_data = boards[board_num]
        
        print(f"Board {board_num}...", end=' ', flush=True)
        
        dd_analysis = calculate_dd_for_hand(board_data)
        
        if dd_analysis:
            boards[board_num]['dd_analysis'] = dd_analysis
            updated_count += 1
            print("✓")
            
            # Show sample output
            if updated_count <= 3 or updated_count == len(boards):
                print(f"  NT: {dd_analysis.get('NTN', '-')}-{dd_analysis.get('NTS', '-')}-{dd_analysis.get('NTE', '-')}-{dd_analysis.get('NTW', '-')}")
                print(f"  S:  {dd_analysis.get('SN', '-')}-{dd_analysis.get('SS', '-')}-{dd_analysis.get('SE', '-')}-{dd_analysis.get('SW', '-')}")
        else:
            print("✗ (error)")
    
    # Save updated database
    print(f"\nSaving database with {updated_count} updated boards...")
    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("Done! Database updated successfully.")
    print(f"\nRefresh your browser to see the DD tables with correct contract levels.")

if __name__ == '__main__':
    main()
