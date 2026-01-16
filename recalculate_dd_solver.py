#!/usr/bin/env python3
"""
Recalculate Double Dummy analysis for all boards with verified hands
"""

import json
import sys

# Try to import DDS library
try:
    import dds
    print("✓ DDS library found")
except ImportError:
    print("✗ DDS library not installed")
    print("  Installing dds and dds_swiginterface...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "dds", "-q"])
    import dds
    print("✓ DDS library installed")

# Load database
print("\nLoading database...")
with open("app/www/hands_database.json", "r", encoding="utf-8") as f:
    db = json.load(f)

# Get board data
boards = db['events']['hosgoru_04_01_2026']['boards']

print(f"Found {len(boards)} boards\n")

# Process each board
for board_num, board_data in boards.items():
    print(f"Board {board_num}...", end=" ", flush=True)
    
    hands = board_data.get('hands')
    if not hands:
        print("✗ No hands found")
        continue
    
    try:
        # Convert hands to DDS format
        # DDS format: PBN string or similar
        # Create PBN: N:S.H.D.C W:S.H.D.C N:S.H.D.C E:S.H.D.C
        
        n_hand = f"{hands['North']['S']}.{hands['North']['H']}.{hands['North']['D']}.{hands['North']['C']}"
        s_hand = f"{hands['South']['S']}.{hands['South']['H']}.{hands['South']['D']}.{hands['South']['C']}"
        e_hand = f"{hands['East']['S']}.{hands['East']['H']}.{hands['East']['D']}.{hands['East']['C']}"
        w_hand = f"{hands['West']['S']}.{hands['West']['H']}.{hands['West']['D']}.{hands['West']['C']}"
        
        # Create DDS table
        dealer = board_data.get('dealer', 'N')
        vuln = board_data.get('vulnerability', 'None')
        
        # Dealer code: 0=N, 1=E, 2=S, 3=W
        dealer_map = {'N': 0, 'E': 1, 'S': 2, 'W': 3}
        dealer_code = dealer_map.get(dealer, 0)
        
        # Vulnerability code: 0=None, 1=N-S, 2=E-W, 3=All
        vuln_map = {
            'None': 0,
            'N-S': 1,
            'E-W': 2,
            'All': 3
        }
        vuln_code = vuln_map.get(vuln, 0)
        
        # Create DDS table
        table = dds.ddTableDeal()
        table.cards = dds.holdings2PBN(
            north=n_hand,
            east=e_hand,
            south=s_hand,
            west=w_hand
        )
        
        # Calculate DD tricks
        result = dds.ddTable(table.cards, dealer_code, vuln_code)
        
        # Extract tricks for all denominations and players
        dd_analysis = {}
        suits = ['N', 'S', 'H', 'D', 'C']  # NT, Spades, Hearts, Diamonds, Clubs
        
        for suit_idx, suit in enumerate(suits):
            for player_idx in range(4):
                player = ['N', 'E', 'S', 'W'][player_idx]
                tricks = result[suit_idx][player_idx]
                dd_analysis[f"{suit}{player}"] = tricks
        
        # Update database
        board_data['dd_analysis'] = dd_analysis
        print(f"✓ {len(dd_analysis)} entries")
        
    except Exception as e:
        print(f"✗ Error: {str(e)[:50]}")

# Save updated database
print("\n✓ Saving updated database...")
with open("app/www/hands_database.json", "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print("✓ Complete! DD analysis recalculated for all boards")

# Show sample
print("\nSample Board 1 DD Analysis:")
dd = boards['1'].get('dd_analysis', {})
suits = ['N', 'S', 'H', 'D', 'C']
print("     N  E  S  W")
for suit in suits:
    tricks = [dd.get(f"{suit}{p}", "-") for p in ['N', 'E', 'S', 'W']]
    print(f"{suit}: {tricks[0]}  {tricks[1]}  {tricks[2]}  {tricks[3]}")
