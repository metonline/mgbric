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

def rotate_hands(hands_list, dealer_pos):
    """
    Rotate hands based on dealer position.
    In LIN format with dealer position N (1-4):
    - md|1: dealer=N, hands listed as N,E,S
    - md|2: dealer=E, hands listed as W,E,S (partner, dealer, RHO)
    - md|3: dealer=S, hands listed as W,S,E (partner relative to S)
    - md|4: dealer=W, hands listed as W,N,E (partner, dealer, RHO)
    
    Actually, testing with Board 10:
    - md|2 with AK75(W),Q64(E),832(S) matches vugraph
    - So hands are listed as: [opposite/partner], [dealer], [RHO]
    """
    h1, h2, h3 = hands_list
    
    if dealer_pos == 1:  # North is dealer
        return {'N': h1, 'E': h2, 'S': h3}
    elif dealer_pos == 2:  # East is dealer
        return {'W': h1, 'E': h2, 'S': h3}
    elif dealer_pos == 3:  # South is dealer
        return {'W': h1, 'S': h2, 'E': h3}
    elif dealer_pos == 4:  # West is dealer
        return {'W': h1, 'N': h2, 'E': h3}

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
            # Rotate hands based on dealer position
            rotated = rotate_hands(hands_list, dealer_pos)
            
            # Calculate missing hand
            n_hand = rotated.get('N', None)
            e_hand = rotated.get('E', None)
            s_hand = rotated.get('S', None)
            w_hand = rotated.get('W', None)
            
            if not n_hand:
                n_hand = calculate_fourth_hand(e_hand, s_hand, w_hand) if e_hand and s_hand and w_hand else None
            elif not e_hand:
                e_hand = calculate_fourth_hand(n_hand, s_hand, w_hand) if n_hand and s_hand and w_hand else None
            elif not s_hand:
                s_hand = calculate_fourth_hand(n_hand, e_hand, w_hand) if n_hand and e_hand and w_hand else None
            elif not w_hand:
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

# Update database
if len(hands_from_lin) > 0:
    event_key = f"405376_{event_date}"
    if event_key not in database:
        database[event_key] = {}
    
    for board_num, hands in hands_from_lin.items():
        board_key = f"Board {board_num}"
        database[event_key][board_key] = hands
    
    # Save database
    with open('hands_database.json', 'w') as f:
        json.dump(database, f, indent=2)
    
    print(f"Updated database for event {event_key}")
    print(f"Total hands in database: {sum(len(boards) for boards in database.values())}")
