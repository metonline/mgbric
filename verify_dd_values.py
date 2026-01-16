#!/usr/bin/env python3
"""
Test DD Analysis values by displaying hands and current database values
Then we can manually verify or use an online solver
"""

import json

# Load the database
with open('app/www/hands_database.json', 'r', encoding='utf-8') as f:
    database = json.load(f)

boards_data = database['events']['hosgoru_04_01_2026']['boards']

print("=" * 80)
print("DD ANALYSIS VERIFICATION")
print("=" * 80)
print("\nTo verify DD values, you can:")
print("1. Use BridgeBase online solver")
print("2. Use DealMaster or other bridge software")
print("3. Use the Vugraph hands which are verified correct")
print("\n" + "=" * 80)

test_boards = [1, 2, 3]

for board_num in test_boards:
    board_key = str(board_num)
    if board_key not in boards_data:
        continue
    
    board_data = boards_data[board_key]
    hands = board_data['hands']
    current_dd = board_data.get('dd_analysis', {})
    
    print(f"\nBOARD {board_num}")
    print(f"Dealer: {board_data['dealer']} | Vulnerability: {board_data['vulnerability']}")
    print("-" * 80)
    
    # Format hands for easy reading
    print(f"North: ♠{hands['North']['S']} ♥{hands['North']['H']} ♦{hands['North']['D']} ♣{hands['North']['C']}")
    print(f"East:  ♠{hands['East']['S']} ♥{hands['East']['H']} ♦{hands['East']['D']} ♣{hands['East']['C']}")
    print(f"South: ♠{hands['South']['S']} ♥{hands['South']['H']} ♦{hands['South']['D']} ♣{hands['South']['C']}")
    print(f"West:  ♠{hands['West']['S']} ♥{hands['West']['H']} ♦{hands['West']['D']} ♣{hands['West']['C']}")
    
    print(f"\nCurrent DD Values in Database:")
    print(f"{'Suit':<6} {'N':<4} {'E':<4} {'S':<4} {'W':<4}")
    print("-" * 24)
    
    suits = ['NT', 'S', 'H', 'D', 'C']
    for suit in suits:
        n_tricks = current_dd.get(f'N{suit}', '?')
        e_tricks = current_dd.get(f'E{suit}', '?')
        s_tricks = current_dd.get(f'S{suit}', '?')
        w_tricks = current_dd.get(f'W{suit}', '?')
        print(f"{suit:<6} {n_tricks:<4} {e_tricks:<4} {s_tricks:<4} {w_tricks:<4}")
    
    # Get board results for context
    results = board_data.get('results', [])
    if results:
        print(f"\nSample Results (first 3):")
        for i, result in enumerate(results[:3]):
            print(f"  Pair {result.get('pair_num', '?')}: {result.get('contract', '?')} by {result.get('direction', '?')}")

print("\n" + "=" * 80)
print("VERIFICATION INSTRUCTIONS")
print("=" * 80)
print("""
To check if DD values are correct:

1. MANUAL CHECK:
   - Go to https://www.bridgebase.com/
   - Enter the hands in a deal
   - Check the DD table values

2. CHECK AGAINST ACTUAL PLAY:
   - Look at the contracts played
   - See if they make sense given the DD values
   - For example, if a contract failed, check if it should have in DD

3. COMMON ISSUES:
   - Make sure North is leader (North = player 1)
   - Verify suit symbols (S=♠, H=♥, D=♦, C=♣)
   - Check that all 13 cards are accounted for

Current sample shows:
- Board 1: Database has NT tricks N=9, E=4, S=9, W=4 (and other suits)
- Board 2: Database has NT tricks N=8, E=5, S=8, W=5 (and other suits)
- Board 3: Database has NT tricks N=8, E=5, S=8, W=5 (and other suits)
""")
