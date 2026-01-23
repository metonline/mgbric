import json

# Load the database
with open('hands_database.json', 'r', encoding='utf-8') as f:
    hands_data = json.load(f)

# All 52 cards in each suit
all_cards = 'AKQJT98765432'

def calculate_remaining_hand(e_hand, s_hand, w_hand):
    """Calculate N's hand from remaining cards after E, S, W"""
    e_suits = e_hand.split('.')
    s_suits = s_hand.split('.')
    w_suits = w_hand.split('.')
    
    n_suits = []
    for suit_idx in range(4):
        # Get cards used by E, S, W in this suit
        used_cards = e_suits[suit_idx] + s_suits[suit_idx] + w_suits[suit_idx]
        # Calculate remaining cards for N
        n_suit = ''.join(c for c in all_cards if c not in used_cards)
        n_suits.append(n_suit)
    
    return '.'.join(n_suits)

# Update Board 2 with the correct hands
for board in hands_data:
    if board['board'] == 2:
        # E, S, W are given; calculate N
        e_hand = 'KT54.K98.K763.K5'
        s_hand = '732.QT7.A9.J8764'
        w_hand = 'QJ96.J6.JT82.AQT'
        n_hand = calculate_remaining_hand(e_hand, s_hand, w_hand)
        
        # Store in correct N-E-S-W order
        board['hands']['N'] = n_hand
        board['hands']['E'] = e_hand
        board['hands']['S'] = s_hand
        board['hands']['W'] = w_hand
        
        # Verify
        n_len = sum(len(s) for s in board['hands']['N'].split('.'))
        e_len = sum(len(s) for s in board['hands']['E'].split('.'))
        s_len = sum(len(s) for s in board['hands']['S'].split('.'))
        w_len = sum(len(s) for s in board['hands']['W'].split('.'))
        total = n_len + e_len + s_len + w_len
        
        print(f"Board 2 updated (E deals):")
        print(f"  N: {board['hands']['N']} ({n_len} cards)")
        print(f"  E: {board['hands']['E']} ({e_len} cards)")
        print(f"  S: {board['hands']['S']} ({s_len} cards)")
        print(f"  W: {board['hands']['W']} ({w_len} cards)")
        print(f"  Total: {total} cards")

# Save the updated database
with open('hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(hands_data, f, indent=2, ensure_ascii=False)

print("\nBoard 2 updated successfully!")
