import json

# All 52 cards in each suit
ALL_CARDS = 'AKQJT98765432'

def calculate_remaining_hand(hand1, hand2, hand3):
    """Calculate 4th hand from remaining cards after 3 hands are given"""
    suits1 = hand1.split('.')
    suits2 = hand2.split('.')
    suits3 = hand3.split('.')
    
    remaining_suits = []
    for suit_idx in range(4):
        used_cards = suits1[suit_idx] + suits2[suit_idx] + suits3[suit_idx]
        remaining = ''.join(c for c in ALL_CARDS if c not in used_cards)
        remaining_suits.append(remaining)
    
    return '.'.join(remaining_suits)

def rotate_hands_by_dealer(hand_in_dealer_order, dealer):
    """
    Rotate hands from dealer-relative order to N-E-S-W order.
    
    hand_in_dealer_order: list of 3 hands [dealer_hand, next_hand, next_next_hand]
    dealer: 'N', 'E', 'S', or 'W'
    
    Returns: dict with 'N', 'E', 'S', 'W' keys
    """
    hands_from_dealer = {
        'N': {'N': 0, 'E': 1, 'S': 2},  # N deals: hand[0]=N, hand[1]=E, hand[2]=S
        'E': {'E': 0, 'S': 1, 'W': 2},  # E deals: hand[0]=E, hand[1]=S, hand[2]=W
        'S': {'S': 0, 'W': 1, 'N': 2},  # S deals: hand[0]=S, hand[1]=W, hand[2]=N
        'W': {'W': 0, 'N': 1, 'E': 2},  # W deals: hand[0]=W, hand[1]=N, hand[2]=E
    }
    
    mapping = hands_from_dealer[dealer]
    result = {}
    
    for direction, index in mapping.items():
        result[direction] = hand_in_dealer_order[index]
    
    return result

def update_board_hands(board_data, dealer, hand_from_dealer, hand_after_dealer, hand_after_that):
    """
    Update a board's hands given 3 hands in dealer order.
    Calculates the 4th hand (the one not given) from remaining cards.
    
    board_data: the board dict to update
    dealer: 'N', 'E', 'S', or 'W'
    hand_from_dealer: hand string for dealer
    hand_after_dealer: hand string for next player after dealer
    hand_after_that: hand string for next player
    """
    # Rotate to N-E-S-W order
    rotated = rotate_hands_by_dealer(
        [hand_from_dealer, hand_after_dealer, hand_after_that],
        dealer
    )
    
    # Find which position is missing
    dealer_positions = {
        'N': ['N', 'E', 'S'],  # Missing W
        'E': ['E', 'S', 'W'],  # Missing N
        'S': ['S', 'W', 'N'],  # Missing E
        'W': ['W', 'N', 'E'],  # Missing S
    }
    
    given_positions = dealer_positions[dealer]
    all_positions = ['N', 'E', 'S', 'W']
    missing_position = [p for p in all_positions if p not in given_positions][0]
    
    # Calculate missing hand
    given_hands = [rotated[p] for p in given_positions]
    missing_hand = calculate_remaining_hand(given_hands[0], given_hands[1], given_hands[2])
    rotated[missing_position] = missing_hand
    
    # Update board
    board_data['hands'] = rotated
    return board_data

# Load database
with open('hands_database.json', 'r', encoding='utf-8') as f:
    hands_data = json.load(f)

# Define all board hands data
# Format: (board_num, dealer, hand1, hand2, hand3)
# where hand1=dealer's hand, hand2=next player, hand3=next player
# (4th hand will be calculated automatically)

boards_data = [
    (1, 'N', 'K86.QJT7.AQT.832', '975.A53.KJ93.J76', 'T42.2.8542.KQT54'),
    (2, 'E', 'KT54.K98.K763.K5', '732.QT7.A9.J8764', 'QJ96.J6.JT82.AQT'),
    # Add more boards here following the same pattern
]

# Update boards
updated_count = 0
for board_num, dealer, hand1, hand2, hand3 in boards_data:
    for board in hands_data:
        if board['board'] == board_num:
            update_board_hands(board, dealer, hand1, hand2, hand3)
            
            # Verify
            n_len = sum(len(s) for s in board['hands']['N'].split('.'))
            e_len = sum(len(s) for s in board['hands']['E'].split('.'))
            s_len = sum(len(s) for s in board['hands']['S'].split('.'))
            w_len = sum(len(s) for s in board['hands']['W'].split('.'))
            total = n_len + e_len + s_len + w_len
            
            print(f"Board {board_num} ({dealer} deals): ✓ Total={total} cards")
            print(f"  N: {board['hands']['N']} ({n_len})")
            print(f"  E: {board['hands']['E']} ({e_len})")
            print(f"  S: {board['hands']['S']} ({s_len})")
            print(f"  W: {board['hands']['W']} ({w_len})")
            updated_count += 1
            break

# Save
with open('hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(hands_data, f, indent=2, ensure_ascii=False)

print(f"\n✓ Updated {updated_count} boards successfully!")
