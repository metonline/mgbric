#!/usr/bin/env python3
"""
Export hands in a format suitable for the BridgeWebs DD solver
https://dds.bridgewebs.com/bsol_standalone/ddummy.htm

This generates a file with all hands formatted for quick batch processing
"""

import json
import os

# Try to find the original database (before my incorrect fix)
backup_files = [
    'app/www/hands_database.json.bak',
    'app/www/hands_database.json',
]

database_file = None
for f in backup_files:
    if os.path.exists(f):
        database_file = f
        break

if not database_file:
    print("Error: Could not find database file")
    exit(1)

print(f"Using: {database_file}")

with open(database_file, 'r', encoding='utf-8') as f:
    database = json.load(f)

boards_data = database['events']['hosgoru_04_01_2026']['boards']

print("=" * 100)
print("HANDS EXPORT FOR DD SOLVER")
print("=" * 100)
print("\nFormat for BridgeWebs DD Solver:")
print("https://dds.bridgewebs.com/bsol_standalone/ddummy.htm")
print("\nPaste each hand into the solver to get correct DD values\n")

output_file = 'dd_solver_input.txt'

with open(output_file, 'w', encoding='utf-8') as out:
    for board_num in range(1, 31):
        board_key = str(board_num)
        if board_key not in boards_data:
            continue
        
        board_data = boards_data[board_key]
        hands = board_data['hands']
        dealer = board_data['dealer']
        vuln = board_data['vulnerability']
        
        # Format: N: S.H.D.C E: S.H.D.C W: S.H.D.C S: S.H.D.C
        n_hand = f"{hands['North']['S']}.{hands['North']['H']}.{hands['North']['D']}.{hands['North']['C']}"
        e_hand = f"{hands['East']['S']}.{hands['East']['H']}.{hands['East']['D']}.{hands['East']['C']}"
        w_hand = f"{hands['West']['S']}.{hands['West']['H']}.{hands['West']['D']}.{hands['West']['C']}"
        s_hand = f"{hands['South']['S']}.{hands['South']['H']}.{hands['South']['D']}.{hands['South']['C']}"
        
        out.write(f"BOARD {board_num}\n")
        out.write(f"Dealer: {dealer} | Vulnerability: {vuln}\n")
        out.write(f"N: {n_hand}\n")
        out.write(f"E: {e_hand}\n")
        out.write(f"W: {w_hand}\n")
        out.write(f"S: {s_hand}\n")
        out.write("\n")
        
        # Also print to console
        print(f"BOARD {board_num} (Dealer: {dealer}, Vuln: {vuln})")
        print(f"N: {n_hand}")
        print(f"E: {e_hand}")
        print(f"W: {w_hand}")
        print(f"S: {s_hand}")
        print()

print("\n" + "=" * 100)
print(f"✓ All hands exported to: {output_file}")
print("\nINSTRUCTIONS:")
print("1. Go to: https://dds.bridgewebs.com/bsol_standalone/ddummy.htm")
print("2. For each board:")
print("   - Enter N, E, W, S hands")
print("   - Select dealer and vulnerability")
print("   - Click 'Calculate DD Table'")
print("   - Copy the DD values")
print("3. Update hands_database.json with the correct DD values")
print("\nOr manually enter into the solver one at a time.")
