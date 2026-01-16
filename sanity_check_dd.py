#!/usr/bin/env python3
"""
Simple DD sanity check - verify if values seem reasonable
"""

import json

with open('app/www/hands_database.json', 'r', encoding='utf-8') as f:
    database = json.load(f)

boards_data = database['events']['hosgoru_04_01_2026']['boards']

print("=" * 80)
print("DD VALUES SANITY CHECK")
print("=" * 80)
print("\nChecking if DD values make mathematical sense:")
print("- If N makes X tricks in a suit, E should make 13-X tricks")
print("- Similarly for S vs W\n")

issues_found = []

for board_num in range(1, 31):
    board_key = str(board_num)
    if board_key not in boards_data:
        continue
    
    board_data = boards_data[board_key]
    dd = board_data.get('dd_analysis', {})
    
    if not dd:
        continue
    
    suits = ['N', 'S', 'H', 'D', 'C']
    
    for suit in suits:
        n_key = f'N{suit}'
        e_key = f'E{suit}'
        s_key = f'S{suit}'
        w_key = f'W{suit}'
        
        if all(key in dd for key in [n_key, e_key, s_key, w_key]):
            n_tricks = dd[n_key]
            e_tricks = dd[e_key]
            s_tricks = dd[s_key]
            w_tricks = dd[w_key]
            
            # Check if complementary
            # In bridge, N+E tricks should equal S+W tricks = 13
            # And N+S should roughly equal E+W
            
            ne_total = n_tricks + e_tricks
            sw_total = s_tricks + w_tricks
            
            if ne_total != 13 or sw_total != 13:
                issues_found.append({
                    'board': board_num,
                    'suit': suit,
                    'detail': f"N+E={ne_total}, S+W={sw_total} (should both be 13)"
                })

if issues_found:
    print("❌ ISSUES FOUND WITH DD VALUES:\n")
    for issue in issues_found[:10]:  # Show first 10
        print(f"Board {issue['board']:2d} {issue['suit']}: {issue['detail']}")
    print(f"\nTotal issues found: {len(issues_found)}")
else:
    print("✓ All DD values pass basic sanity checks")
    print("  (N+E = 13 and S+W = 13 for each suit)")

print("\n" + "=" * 80)
print("NEXT STEP: Manual verification")
print("=" * 80)
print("""
Since the values pass basic checks, please verify them manually by:

1. Go to https://www.bridgebase.com/tools/dd-table
2. Enter the hands for Board 1:
   North: ♠Q864 ♥J97 ♦T3 ♣A842
   East:  ♠AKJT93 ♥Q ♦QJ854 ♣T
   South: ♠7 ♥A53 ♦K97 ♣J97653
   West:  ♠52 ♥KT8642 ♦A62 ♣KQ

3. Compare the calculated DD table with database values

If there are differences, the database needs to be updated.
""")
