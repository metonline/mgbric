#!/usr/bin/env python3
"""
Calculate Double Dummy (DD) values for all 30 boards using PyDDS solver.
Updates hands_database.json with calculated trick values (6-13).
"""

import json
import sys
try:
    from pydds.dds import DDSTable
except ImportError:
    print("ERROR: PyDDS not installed. Run: pip install pydds")
    sys.exit(1)

def hand_to_dds_format(hands_dict):
    """
    Convert hand dict {N: {...}, S: {...}, E: {...}, W: {...}} to DDS format string.
    DDS format: suits in order SHDC, with cards listed high to low within each suit.
    Example: "AKQ...J..9...8..." for each suit
    """
    suits_order = ['S', 'H', 'D', 'C']
    result = ""
    
    for suit in suits_order:
        # Get cards for all players in this suit
        cards_by_player = {}
        for player in ['N', 'S', 'E', 'W']:
            cards_by_player[player] = hands_dict.get(player, {}).get(suit, '')
        
        # Combine all cards in this suit
        all_cards = ''.join(cards_by_player.values())
        result += all_cards if all_cards else '.'
    
    return result

def calculate_dd_tricks(board_data):
    """
    Calculate DD tricks for a board using PyDDS.
    Returns dict with keys like 'NTS', 'NTE', etc. containing tricks (6-13).
    """
    try:
        hands = board_data.get('hands', {})
        if not hands:
            print(f"  WARNING: No hands data")
            return None
        
        # Get dealer and vulnerability
        dealer = board_data.get('dealer', 'N')
        vulnerability = board_data.get('vulnerability', 'None')
        
        # Convert vulnerability to DDS format (0=none, 1=N-S, 2=E-W, 3=both)
        vuln_map = {'None': 0, 'N-S': 1, 'E-W': 2, 'Both': 3}
        vuln = vuln_map.get(vulnerability, 0)
        
        # Convert dealer to number (0=N, 1=E, 2=S, 3=W)
        dealer_map = {'N': 0, 'E': 1, 'S': 2, 'W': 3}
        dealer_num = dealer_map.get(dealer, 0)
        
        # Create DDS table
        table = DDSTable()
        
        # Set the hands (format: N hand, S hand, E hand, W hand)
        # Each hand is a 52-character string representing all cards
        pbn_hands = {
            'N': hands.get('N', {}),
            'S': hands.get('S', {}),
            'E': hands.get('E', {}),
            'W': hands.get('W', {}),
        }
        
        # Convert to DDS format: each suit as string of cards
        for player in ['N', 'S', 'E', 'W']:
            player_hand = pbn_hands.get(player, {})
            hand_string = hand_to_dds_format({player: player_hand})
            # Set hand in DDS table
        
        # Actually, let's use a simpler approach - construct the PBN string
        pbn = "N:"
        for suit in ['S', 'H', 'D', 'C']:
            cards = ''
            for player in ['N', 'S', 'E', 'W']:
                cards += pbn_hands[player].get(suit, '')
            pbn += cards + " "
        
        table.SetupPBN(pbn, dealer_num, vuln)
        table.CalcDDtable()
        results = table.GetDDtable()
        
        # Convert results to trick values (6-13)
        # Results are indexed: [strain][player] where strain 0=NT, 1=S, 2=H, 3=D, 4=C
        # and player 0=N, 1=S, 2=E, 3=W
        strain_names = ['NT', 'S', 'H', 'D', 'C']
        player_names = ['N', 'S', 'E', 'W']
        
        dd_analysis = {}
        for strain_idx, strain in enumerate(strain_names):
            for player_idx, player in enumerate(player_names):
                tricks = results[strain_idx][player_idx]
                key = f"{strain}{player}"
                # Tricks are 0-13, we want 6-13 (6 = pass/no tricks, 13 = all tricks)
                # Actually PyDDS returns tricks directly (0-13), so add 6 if less than 6
                dd_analysis[key] = tricks if tricks >= 6 else tricks + 6
        
        return dd_analysis
    
    except Exception as e:
        print(f"  ERROR calculating DD: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    db_path = 'app/www/hands_database.json'
    
    print("Loading database...")
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    boards = data['events']['hosgoru_04_01_2026']['boards']
    
    print(f"Found {len(boards)} boards")
    print("Calculating DD values using PyDDS solver...\n")
    
    updated_count = 0
    for board_num_str in sorted(boards.keys(), key=lambda x: int(x) if x.isdigit() else 999):
        board = boards[board_num_str]
        print(f"Board {board_num_str}...", end=" ", flush=True)
        
        dd_values = calculate_dd_tricks(board)
        if dd_values:
            board['dd_analysis'] = dd_values
            updated_count += 1
            print("✓")
        else:
            print("✗")
    
    # Save updated database
    print(f"\nSaving updated database...")
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Updated {updated_count}/{len(boards)} boards")
    print(f"Saved to {db_path}")

if __name__ == '__main__':
    main()
