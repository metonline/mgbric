#!/usr/bin/env python3
"""
Export hands from database to LIN format for Bridge Solver analysis
Generates a file you can upload to https://dds.bridgewebs.com/bsol_standalone/ddummy.htm
"""

import json
import urllib.parse

def hand_to_lin_notation(hand):
    """Convert hand dict to LIN notation: SA987HK98DKT5CQ98"""
    lin = ""
    for suit in ['S', 'H', 'D', 'C']:
        lin += suit + hand.get(suit, "")
    return lin

def export_hands_to_lin():
    """Export all hands to LIN format file"""
    
    with open('app/www/hands_database.json', 'r') as f:
        data = json.load(f)
    
    # Get the tournament
    event_data = data['events']['hosgoru_04_01_2026']
    boards = event_data['boards']
    
    # Create LIN file content
    lin_lines = []
    
    for board_num in sorted([int(b) for b in boards.keys()]):
        board_key = str(board_num)
        board = boards[board_key]
        
        hands = board['hands']
        dealer = board['dealer']
        vuln = board['vulnerability']
        
        # Convert vulnerability to LIN format: o=none, n=ns, e=ew, b=both
        vuln_map = {'None': 'o', 'NS': 'n', 'EW': 'e', 'Both': 'b'}
        vuln_code = vuln_map.get(vuln, 'o')
        
        # Get hands in order: N, E, S, W
        n_hand = hand_to_lin_notation(hands['North'])
        e_hand = hand_to_lin_notation(hands['East'])
        s_hand = hand_to_lin_notation(hands['South'])
        w_hand = hand_to_lin_notation(hands['West'])
        
        # Dealer code: 1=N, 2=E, 3=S, 4=W
        dealer_map = {'N': '1', 'E': '2', 'S': '3', 'W': '4'}
        dealer_code = dealer_map.get(dealer, '1')
        
        # LIN format: md|[dealer][N hand],[S hand],[E hand],[W hand]|sv|[vuln]|
        # bd=board number, ah=board heading
        lin_record = f"md|{dealer_code}{n_hand},{s_hand},{e_hand},{w_hand}|sv|{vuln_code}|bd|{board_num}|ah|Board {board_num}|"
        lin_lines.append(lin_record)
    
    # Write to LIN file
    output_file = 'export_hosgoru_04_01_2026.lin'
    with open(output_file, 'w') as f:
        f.write('\n'.join(lin_lines))
    
    print(f"✅ Exported {len(lin_lines)} boards to {output_file}")
    print(f"\n📋 Usage Instructions:")
    print(f"1. Go to: https://dds.bridgewebs.com/bsol_standalone/ddummy.htm")
    print(f"2. Click 'Open a PBN, DLM, or LIN file'")
    print(f"3. Upload: {output_file}")
    print(f"4. Click 'Analyse All' to generate DD analysis")
    print(f"5. Right-click on results and copy/export the DD tricks table")
    print(f"6. Run: python import_dd_results.py")
    print(f"\n📄 First board sample:")
    print(lin_lines[0] if lin_lines else "No boards found")
    
    return output_file

if __name__ == '__main__':
    export_hands_to_lin()
