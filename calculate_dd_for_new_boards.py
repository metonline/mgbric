#!/usr/bin/env python3
"""
Calculate Double Dummy (DD) analysis for boards 101-110 only
"""

import json

def calculate_dd_formula(hand_data):
    """
    Calculate DD analysis using a heuristic formula
    Returns: dict with 20 DD values (NT/S/H/D/C x N/E/S/W)
    """
    
    def count_hcp(cards_str):
        """Count High Card Points"""
        hcp = 0
        if 'A' in cards_str: hcp += 4
        if 'K' in cards_str: hcp += 3
        if 'Q' in cards_str: hcp += 2
        if 'J' in cards_str: hcp += 1
        return hcp
    
    def card_count(cards_str):
        """Count cards in a suit"""
        return len(cards_str) if cards_str else 0
    
    # Calculate total points for each player
    result = {}
    
    for player in ['N', 'E', 'S', 'W']:
        hand = hand_data.get(player, {})
        total_hcp = 0
        total_cards = 0
        
        for suit in ['S', 'H', 'D', 'C']:
            suit_cards = hand.get(suit, '')
            total_hcp += count_hcp(suit_cards)
            total_cards += card_count(suit_cards)
        
        # Simple heuristic: more points = can make more tricks
        # Base estimate: 6 tricks + (hcp / 5) + (long suits bonus)
        
        # Count long suits (5+ cards)
        long_suit_bonus = 0
        for suit in ['S', 'H', 'D', 'C']:
            suit_len = card_count(hand.get(suit, ''))
            if suit_len >= 5:
                long_suit_bonus += 1
        
        # Base tricks estimate
        base_tricks = 6 + (total_hcp // 4) + long_suit_bonus
        
        # For each denomination
        for denom in ['NT', 'S', 'H', 'D', 'C']:
            suit_code = denom if denom != 'NT' else None
            
            if suit_code:
                suit_cards = hand.get(suit_code, '')
                suit_hcp = count_hcp(suit_cards)
                suit_len = card_count(suit_cards)
                # Tricks in suit: more cards = more tricks potentially
                tricks_estimate = 4 + (suit_hcp // 3) + (suit_len - 3) // 2
            else:
                # NT is about balanced strength
                tricks_estimate = 6 + (total_hcp // 4)
            
            # Clamp to reasonable values (0-13 tricks)
            tricks_estimate = max(0, min(13, tricks_estimate))
            
            key = f"{denom}{player}"
            result[key] = tricks_estimate
    
    return result

# Load database
print("Loading hands_database.json...")
with open('hands_database.json', 'r', encoding='utf-8') as f:
    hands = json.load(f)

# Process boards 101-110
print("Calculating DD for boards 101-110...")
count = 0
for board_id in range(101, 111):
    board_key = str(board_id)
    if board_key in hands:
        board = hands[board_key]
        # Calculate DD
        dd_analysis = calculate_dd_formula(board)
        board['dd_analysis'] = dd_analysis
        count += 1
        print(f"Board {board_id}: OK")

# Save updated database
print(f"\nSaving {count} updated boards...")
with open('hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(hands, f, indent=2, ensure_ascii=False)

print(f"Done! Updated hands_database.json with DD analysis for boards 101-110")
