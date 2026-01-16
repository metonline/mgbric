#!/usr/bin/env python3
"""
Manual DD value entry tool
Since online solver isn't working, use this to enter DD values one board at a time
"""

import json

print("""
╔════════════════════════════════════════════════════════════════╗
║          MANUAL DD VALUES INPUT TOOL                           ║
║                                                                ║
║  Since the online solver isn't responding,                     ║
║  you can enter DD values manually here.                        ║
║                                                                ║
║  For each board, enter tricks available for each suit:         ║
║  NT, Spades, Hearts, Diamonds, Clubs                           ║
║  (for players N, E, S, W)                                      ║
╚════════════════════════════════════════════════════════════════╝
""")

with open('app/www/hands_database.json', encoding='utf-8') as f:
    db = json.load(f)

boards = db['events']['hosgoru_04_01_2026']['boards']

# Ask which board to start from
try:
    start_board = int(input("\nWhich board do you want to start from? (1-30, default=1): ") or "1")
except:
    start_board = 1

for board_num in range(start_board, 31):
    board = boards[str(board_num)]
    
    print(f"\n{'='*60}")
    print(f"BOARD {board_num} - Dealer: {board['dealer']}, Vuln: {board['vulnerability']}")
    print(f"{'='*60}")
    
    print("\nEnter tricks available for each strain:")
    print("(Enter as: NT Spades Hearts Diamonds Clubs)")
    print("Example: 9 8 9 8 7")
    
    while True:
        try:
            # Get input for all 4 players
            print("\nNorth tricks (NT S H D C):", end=" ")
            n_tricks = list(map(int, input().split()))
            if len(n_tricks) != 5:
                print("  ✗ Need 5 values")
                continue
            
            print("East tricks (NT S H D C):  ", end=" ")
            e_tricks = list(map(int, input().split()))
            if len(e_tricks) != 5:
                print("  ✗ Need 5 values")
                continue
            
            print("South tricks (NT S H D C): ", end=" ")
            s_tricks = list(map(int, input().split()))
            if len(s_tricks) != 5:
                print("  ✗ Need 5 values")
                continue
            
            print("West tricks (NT S H D C):  ", end=" ")
            w_tricks = list(map(int, input().split()))
            if len(w_tricks) != 5:
                print("  ✗ Need 5 values")
                continue
            
            # Validate - should sum to 13 for complementary positions
            for suit_idx in range(5):
                ns_sum = n_tricks[suit_idx] + s_tricks[suit_idx]
                ew_sum = e_tricks[suit_idx] + w_tricks[suit_idx]
                if ns_sum != 13 or ew_sum != 13:
                    print(f"\n  ✗ Invalid - Suit {['NT','S','H','D','C'][suit_idx]}:")
                    print(f"      N+S = {ns_sum} (should be 13)")
                    print(f"      E+W = {ew_sum} (should be 13)")
                    break
            else:
                # All valid!
                print("\n  ✓ Values accepted")
                break
        
        except (ValueError, IndexError):
            print("  ✗ Invalid input - use space-separated numbers")
        except KeyboardInterrupt:
            print("\n\nCancelled.")
            exit()
    
    # Store DD values
    # Format: "NT": {"N": 9, "E": 4, "S": 9, "W": 4}, etc
    board['dd_analysis'] = {
        'NT': {'N': n_tricks[0], 'E': e_tricks[0], 'S': s_tricks[0], 'W': w_tricks[0]},
        'S':  {'N': n_tricks[1], 'E': e_tricks[1], 'S': s_tricks[1], 'W': w_tricks[1]},
        'H':  {'N': n_tricks[2], 'E': e_tricks[2], 'S': s_tricks[2], 'W': w_tricks[2]},
        'D':  {'N': n_tricks[3], 'E': e_tricks[3], 'S': s_tricks[3], 'W': w_tricks[3]},
        'C':  {'N': n_tricks[4], 'E': e_tricks[4], 'S': s_tricks[4], 'W': w_tricks[4]}
    }
    
    # Ask if continue
    if board_num < 30:
        cont = input(f"\nContinue to Board {board_num + 1}? (y/n): ").lower()
        if cont != 'y':
            break

# Save updated database
with open('app/www/hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print("\n✓ Database updated with DD values!")
