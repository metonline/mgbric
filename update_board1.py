import json

# Load the database
with open('hands_database.json', 'r', encoding='utf-8') as f:
    hands_data = json.load(f)

# All 52 cards in each suit
all_cards = 'AKQJT98765432'

def calculate_west_hand(n_hand, e_hand, s_hand):
    """Calculate West's hand from remaining cards"""
    n_suits = n_hand.split('.')
    e_suits = e_hand.split('.')
    s_suits = s_hand.split('.')
    
    w_suits = []
    for suit_idx in range(4):
        # Get cards in this suit from N, E, S
        used_cards = n_suits[suit_idx] + e_suits[suit_idx] + s_suits[suit_idx]
        # Calculate remaining cards for West
        w_suit = ''.join(c for c in all_cards if c not in used_cards)
        w_suits.append(w_suit)
    
    return '.'.join(w_suits)

# Update Board 1 with the correct hands
for board in hands_data:
    if board['board'] == 1:
        # Set the correct hands
        board['hands']['N'] = 'K86.QJT7.AQT.832'
        board['hands']['E'] = '975.A53.KJ93.J76'
        board['hands']['S'] = 'T42.2.8542.KQT54'
        
        # Recalculate W from remaining cards
        w_hand = calculate_west_hand(
            board['hands']['N'],
            board['hands']['E'],
            board['hands']['S']
        )
        board['hands']['W'] = w_hand
        
        # Verify
        n_len = sum(len(s) for s in board['hands']['N'].split('.'))
        e_len = sum(len(s) for s in board['hands']['E'].split('.'))
        s_len = sum(len(s) for s in board['hands']['S'].split('.'))
        w_len = sum(len(s) for s in board['hands']['W'].split('.'))
        total = n_len + e_len + s_len + w_len
        
        print(f"Board 1 updated:")
        print(f"  N: {board['hands']['N']} ({n_len} cards)")
        print(f"  E: {board['hands']['E']} ({e_len} cards)")
        print(f"  S: {board['hands']['S']} ({s_len} cards)")
        print(f"  W: {board['hands']['W']} ({w_len} cards)")
        print(f"  Total: {total} cards")

# Save the updated database
with open('hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(hands_data, f, indent=2, ensure_ascii=False)

print("\nBoard 1 updated successfully!")
