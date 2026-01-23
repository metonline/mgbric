import json
import re

def calculate_fourth_hand(n, e, s):
    """Calculate W hand from N, E, S using 52-card deck"""
    all_suits = {
        'S': list('AKQJT98765432'),
        'H': list('AKQJT98765432'),
        'D': list('AKQJT98765432'),
        'C': list('AKQJT98765432')
    }
    
    def parse_hand(hand_str):
        """Parse PBN hand notation like 'K86.QJT7.AQT.832'"""
        suits_list = hand_str.split('.')
        used = {'S': set(), 'H': set(), 'D': set(), 'C': set()}
        suit_names = ['S', 'H', 'D', 'C']
        for idx, suit_str in enumerate(suits_list):
            for rank in suit_str:
                used[suit_names[idx]].add(rank)
        return used
    
    n_cards = parse_hand(n)
    e_cards = parse_hand(e)
    s_cards = parse_hand(s)
    
    # Build W's hand from remaining cards
    w_hand = {'S': [], 'H': [], 'D': [], 'C': []}
    for suit in ['S', 'H', 'D', 'C']:
        for rank in all_suits[suit]:
            if rank not in n_cards[suit] and rank not in e_cards[suit] and rank not in s_cards[suit]:
                w_hand[suit].append(rank)
    
    return f"{''.join(w_hand['S'])}.{''.join(w_hand['H'])}.{''.join(w_hand['D'])}.{''.join(w_hand['C'])}"

def parse_hands_by_dealer(hand1, hand2, hand3, dealer_pos):
    """
    Parse hands based on dealer position with proper rotation.
    
    Pattern discovered:
    - md|1 (N dealer): hands = [N], [E], [S] (positions 1, 2, 3)
    - md|2 (E dealer): hands = [W], [E], [S] (positions 4, 2, 3)
    - md|3 (S dealer): hands = [W], [S], [E] (positions 4, 3, 2)
    - md|4 (W dealer): hands = [W], [N], [E] (positions 4, 1, 2)
    
    The pattern for dealer > 1 is: [opposite], [dealer], [next clockwise]
    For dealer = 1, it's just: [dealer], [next], [next]
    """
    
    if dealer_pos == 1:  # North (N=1) is dealer
        # List order: N(1), E(2), S(3)
        return {'N': hand1, 'E': hand2, 'S': hand3}
    
    elif dealer_pos == 2:  # East (E=2) is dealer
        # Opposite=W(4), Dealer=E(2), Next CW from E=S(3)
        # List order: W(4), E(2), S(3)
        return {'W': hand1, 'E': hand2, 'S': hand3}
    
    elif dealer_pos == 3:  # South (S=3) is dealer
        # Opposite=N(1), Dealer=S(3), Next CW from S=W(4)
        # But pattern seems to be: W, S, E based on "skipping" logic
        # List order: W(4), S(3), E(2)
        return {'W': hand1, 'S': hand2, 'E': hand3}
    
    elif dealer_pos == 4:  # West (W=4) is dealer
        # Opposite=E(2), Dealer=W(4), Next CW from W=N(1)
        # List order: W(4), N(1), E(2)
        return {'W': hand1, 'N': hand2, 'E': hand3}

# Read LIN file
with open('event_405376.lin', 'r') as f:
    lin_content = f.read()

# Read database
with open('hands_database.json', 'r') as f:
    database = json.load(f)

hands_from_lin = {}
event_date = "20.01.2026"

for line in lin_content.split('\n'):
    if not line.strip():
        continue
    
    # Extract board number from 'ah|Board (\d+)|'
    board_match = re.search(r'\|ah\|Board (\d+)\|', line)
    
    # Extract hands from 'md|[1-4](.*?)\|sv'
    hands_match = re.search(r'md\|([1-4])(.*?)\|sv', line)
    
    if board_match and hands_match:
        board_num = int(board_match.group(1))
        dealer_pos = int(hands_match.group(1))
        hands_str = hands_match.group(2)
        hands_list = hands_str.split(',')
        
        if len(hands_list) == 3:
            hand1, hand2, hand3 = hands_list
            
            # Parse hands based on dealer position
            compass_hands = parse_hands_by_dealer(hand1, hand2, hand3, dealer_pos)
            
            # Get three known hands
            n_hand = compass_hands.get('N')
            e_hand = compass_hands.get('E')
            s_hand = compass_hands.get('S')
            w_hand = compass_hands.get('W')
            
            # Calculate the missing hand
            if not n_hand and e_hand and s_hand and w_hand:
                n_hand = calculate_fourth_hand(e_hand, s_hand, w_hand)
            elif not e_hand and n_hand and s_hand and w_hand:
                e_hand = calculate_fourth_hand(n_hand, s_hand, w_hand)
            elif not s_hand and n_hand and e_hand and w_hand:
                s_hand = calculate_fourth_hand(n_hand, e_hand, w_hand)
            elif not w_hand and n_hand and e_hand and s_hand:
                w_hand = calculate_fourth_hand(n_hand, e_hand, s_hand)
            
            hands_from_lin[board_num] = {
                'N': n_hand,
                'E': e_hand,
                'S': s_hand,
                'W': w_hand
            }
            
            print(f"Board {board_num} (dealer={dealer_pos}):")
            print(f"  N: {n_hand}")
            print(f"  E: {e_hand}")
            print(f"  S: {s_hand}")
            print(f"  W: {w_hand}")

print(f"\nExtracted {len(hands_from_lin)} boards from LIN")

# Update database (it's a list of objects)
if len(hands_from_lin) > 0:
    event_id = "405376"
    date = "20.01.2026"
    
    # Update each matching entry in the database
    updated_count = 0
    for entry in database:
        if entry.get("event_id") == event_id and entry.get("date") == date:
            board_num = entry.get("board")
            if board_num in hands_from_lin:
                entry['N'] = hands_from_lin[board_num]['N']
                entry['E'] = hands_from_lin[board_num]['E']
                entry['S'] = hands_from_lin[board_num]['S']
                entry['W'] = hands_from_lin[board_num]['W']
                updated_count += 1
    
    # Save database
    with open('hands_database.json', 'w') as f:
        json.dump(database, f, indent=2)
    
    print(f"Updated {updated_count} hands in database")
    print(f"Total entries in database: {len(database)}")
