#!/usr/bin/env python3
"""
Create a LIN file for Bridge Solver Online DD calculation.
This can be uploaded to: https://dds.bridgewebs.com/bsol_standalone/ddummy.htm
"""

import json

def create_lin_file(output_filename='tournament_boards.lin'):
    """Create a complete LIN file from the database"""
    
    # Load database
    with open('app/www/hands_database.json', 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    event = db['events']['hosgoru_04_01_2026']
    boards = event['boards']
    
    print("\n" + "="*70)
    print("CREATING LIN FILE FOR BRIDGE SOLVER ONLINE".center(70))
    print("="*70)
    
    lin_content = ""
    
    def dealer_to_position(dealer):
        dealer_map = {'N': 1, 'E': 2, 'S': 3, 'W': 4}
        return dealer_map.get(dealer, 1)
    
    def hands_to_lin_format(hands):
        """Convert hands to LIN format: West,North,East"""
        def format_hand(hand_dict):
            result = ""
            for suit in ['S', 'H', 'D', 'C']:
                cards = hand_dict.get(suit, '')
                result += suit + cards
            return result
        
        west_lin = format_hand(hands['West'])
        north_lin = format_hand(hands['North'])
        east_lin = format_hand(hands['East'])
        
        return f"{west_lin},{north_lin},{east_lin}"
    
    def vulnerability_to_code(vuln):
        vuln_map = {
            'None': '0',
            'N-S': '1',
            'E-W': '2',
            'Both': '3'
        }
        return vuln_map.get(vuln, '0')
    
    # Create LIN entries for each board
    for board_num in range(1, 31):
        board_key = str(board_num)
        if board_key not in boards:
            continue
        
        board = boards[board_key]
        dealer = board['dealer']
        vuln = board['vulnerability']
        hands = board['hands']
        
        dealer_pos = dealer_to_position(dealer)
        hands_str = hands_to_lin_format(hands)
        vuln_code = vulnerability_to_code(vuln)
        
        # Create LIN string for this board
        lin_entry = f"qx|o1|md|{dealer_pos}{hands_str}|rh||ah|Board {board_num}|sv|{vuln_code}|pg||"
        lin_content += lin_entry + "\n"
        
        print(f"✓ Board {board_num}: {dealer} dealer, {vuln} vulnerability")
    
    # Write to file
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(lin_content)
    
    print(f"\n✅ Created: {output_filename}")
    print(f"   Size: {len(lin_content)} bytes")
    print(f"   Boards: 30")
    print(f"\n📖 How to use:")
    print(f"   1. Go to: https://dds.bridgewebs.com/bsol_standalone/ddummy.htm")
    print(f"   2. Click: 'Open a PBN, DLM, or LIN file'")
    print(f"   3. Select: {output_filename}")
    print(f"   4. Click: 'Analyse All'")
    print(f"   5. Get DD values for all 30 boards automatically!")
    print(f"\n⚙️  Advanced:")
    print(f"   - Set N/S and E/W display options")
    print(f"   - View makeable contracts")
    print(f"   - Check player accuracy")
    print(f"   - Export results")
    print("="*70)
    
    return lin_content

if __name__ == '__main__':
    create_lin_file('app/www/tournament_boards.lin')
    
    # Also create a version in the app/www directory for easy download
    with open('app/www/tournament_boards.lin', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("\n📁 File saved to: app/www/tournament_boards.lin")
    print("   (Ready to download and upload to Bridge Solver Online)")
