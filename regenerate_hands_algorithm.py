#!/usr/bin/env python3
"""
Generate bridge hands using proper dealing algorithm
Dealer deals to self first, then E, S, W in rotation
"""

import json
import random
from itertools import cycle

# Standard 52-card deck
SUITS = ['S', 'H', 'D', 'C']
RANKS = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']

def create_deck():
    """Create a standard 52-card deck"""
    return [(rank, suit) for suit in SUITS for rank in RANKS]

def get_dealer_order(dealer):
    """Get the dealing order starting from dealer (deals to self first)
    
    Dealer deals to self first, then proceeds: E, S, W, E, S, W...
    Returns the 4-hand ordering
    """
    order = ['N', 'E', 'S', 'W']
    dealer_idx = order.index(dealer)
    # Rotate so dealer is first
    return order[dealer_idx:] + order[:dealer_idx]

def deal_hands(dealer='N', seed=None):
    """Deal 13 cards to each player following proper dealing order
    
    Args:
        dealer: which position deals (N, E, S, W)
        seed: random seed for reproducibility
    
    Returns:
        dict with N, E, S, W as keys, each with a hand string
    """
    if seed is not None:
        random.seed(seed)
    
    # Shuffle deck
    deck = create_deck()
    random.shuffle(deck)
    
    # Get dealing order (dealer deals to self first)
    order = get_dealer_order(dealer)
    
    # Deal 13 cards to each player in order
    hands = {pos: [] for pos in ['N', 'E', 'S', 'W']}
    
    # Deal cards one at a time, cycling through the dealing order
    for i, card in enumerate(deck):
        position = order[i % 4]
        hands[position].append(card)
    
    # Convert to string format (PBN notation)
    result = {}
    for pos in ['N', 'E', 'S', 'W']:
        hand_str = format_hand(hands[pos])
        result[pos] = hand_str
    
    return result

def format_hand(cards):
    """Convert card list to PBN notation (S=AK..., H=QJ..., D=..., C=...)"""
    # Group by suit
    by_suit = {suit: [] for suit in SUITS}
    for rank, suit in cards:
        by_suit[suit].append(rank)
    
    # Sort ranks within each suit
    rank_order = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
    for suit in SUITS:
        by_suit[suit].sort(key=lambda r: rank_order.index(r))
    
    # Format as string
    hand_parts = []
    for suit in SUITS:
        suit_cards = ''.join(by_suit[suit]) if by_suit[suit] else '-'
        hand_parts.append(suit_cards)
    
    return '.'.join(hand_parts)

def regenerate_hands_database():
    """Regenerate all 660 hands with proper dealing algorithm"""
    
    # Load existing database to keep metadata
    with open('hands_database.json', 'r', encoding='utf-8') as f:
        existing_data = json.load(f)
    
    # Group by event_id and board
    by_event_board = {}
    for hand in existing_data:
        event_id = hand.get('event_id')
        board = hand.get('board')
        key = (event_id, board)
        by_event_board[key] = hand
    
    # Get unique events and sort by event_id
    events = sorted(set(h.get('event_id') for h in existing_data))
    
    print(f"Regenerating hands for {len(events)} events, 30 boards each")
    
    updated = 0
    
    for event_idx, event_id in enumerate(events):
        # Use event_id as seed for reproducible random dealing
        event_seed = int(event_id) if event_id.isdigit() else event_idx
        
        for board_num in range(1, 31):
            # Get dealer for this board (rotates N-E-S-W)
            dealers = ['N', 'E', 'S', 'W']
            dealer = dealers[(board_num - 1) % 4]
            
            # Seed based on event and board for reproducibility
            hand_seed = event_seed * 1000 + board_num
            
            # Generate hands
            new_hands = deal_hands(dealer=dealer, seed=hand_seed)
            
            # Update existing record
            key = (event_id, board_num)
            if key in by_event_board:
                hand_record = by_event_board[key]
                hand_record['N'] = new_hands['N']
                hand_record['E'] = new_hands['E']
                hand_record['S'] = new_hands['S']
                hand_record['W'] = new_hands['W']
                hand_record['dealer'] = dealer
                # Clear DD analysis since hands changed
                hand_record['dd_analysis'] = None
                hand_record['optimum'] = None
                hand_record['lott'] = None
                updated += 1
    
    # Convert back to list
    hands_list = list(by_event_board.values())
    
    # Save
    with open('hands_database.json', 'w', encoding='utf-8') as f:
        json.dump(hands_list, f, indent=2, ensure_ascii=False)
    
    print(f"Updated {updated}/660 hands with proper dealing algorithm")
    print(f"Saved to hands_database.json")
    print("\nNOTE: DD analysis needs to be recalculated!")
    print("Run: python double_dummy/dd_solver.py --update-db")

if __name__ == '__main__':
    regenerate_hands_database()
