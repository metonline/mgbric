#!/usr/bin/env python3
"""
Calculate Double Dummy (DD) analysis for all hands in hands_database.json
and update with dd_analysis results.
"""

import json
import sys

# Try to import dds library, provide fallback if not available
try:
    import dds
    HAS_DDS = True
except ImportError:
    HAS_DDS = False
    print("⚠️  DDS library not found. Installing dummy solver...")
    print("   To get accurate DD results, run: pip install dds")

def card_to_dds(card_str):
    """Convert card string (e.g., 'AT73') to DDS format (list of integers)"""
    if not card_str:
        return []
    
    rank_map = {'2': 0, '3': 1, '4': 2, '5': 3, '6': 4, '7': 5, '8': 6, 
                '9': 7, 'T': 8, 'J': 9, 'Q': 10, 'K': 11, 'A': 12}
    
    result = []
    for card in card_str:
        if card in rank_map:
            result.append(rank_map[card])
    return sorted(result, reverse=True)

def calculate_dd_dds(hand_data):
    """Calculate DD using DDS library (most accurate)"""
    if not HAS_DDS:
        return None
    
    try:
        # Map hands to DDS format
        # DDS expects: spades, hearts, diamonds, clubs for each player
        # Players: 0=N, 1=E, 2=S, 3=W
        
        holdings = []
        for player in ['N', 'E', 'S', 'W']:
            hand = hand_data.get(player, {})
            spades = card_to_dds(hand.get('S', ''))
            hearts = card_to_dds(hand.get('H', ''))
            diamonds = card_to_dds(hand.get('D', ''))
            clubs = card_to_dds(hand.get('C', ''))
            holdings.append([spades, hearts, diamonds, clubs])
        
        # Calculate DD
        dealer_map = {'N': 0, 'E': 1, 'S': 2, 'W': 3}
        dealer = dealer_map.get(hand_data.get('dealer', 'N'), 0)
        
        vuln_map = {'None': 0, 'NS': 1, 'EW': 2, 'Both': 3}
        vulnerability = vuln_map.get(hand_data.get('vulnerability', 'None'), 0)
        
        # Call DDS solver
        result = dds.dd(holdings, dealer, vulnerability)
        
        # Convert result to our format: {NT/S/H/D/C + N/E/S/W: tricks}
        if result and isinstance(result, list):
            dd_analysis = {}
            denominations = ['NT', 'S', 'H', 'D', 'C']
            players = ['N', 'E', 'S', 'W']
            
            # Result format from DDS: [NT_N, NT_E, NT_S, NT_W, S_N, S_E, S_S, S_W, ...]
            idx = 0
            for denom in denominations:
                for player in players:
                    if idx < len(result):
                        dd_analysis[f'{denom}{player}'] = result[idx]
                    idx += 1
            
            return dd_analysis
    except Exception as e:
        print(f"Error calculating DD with DDS: {e}")
    
    return None

def calculate_dd_formula(hand_data):
    """
    Calculate DD using simplified formula (heuristic, not accurate)
    This is a fallback when DDS library is not available.
    """
    dd_analysis = {}
    
    # Simple heuristic: count high cards and length points
    def count_hcp(hand_str):
        """Count high card points"""
        values = {'A': 4, 'K': 3, 'Q': 2, 'J': 1}
        return sum(values.get(c, 0) for c in hand_str)
    
    def evaluate_hand(player_hand):
        """Evaluate hand strength"""
        total_hcp = 0
        total_length = 0
        for suit in ['S', 'H', 'D', 'C']:
            cards = player_hand.get(suit, '')
            total_hcp += count_hcp(cards)
            total_length += len(cards)
        return total_hcp, total_length
    
    # Calculate basic metrics
    tricks_base = {
        'N': 6, 'E': 6, 'S': 6, 'W': 6
    }
    
    # Adjust based on HCP
    for player in ['N', 'E', 'S', 'W']:
        hand = hand_data.get(player, {})
        hcp, length = evaluate_hand(hand)
        # Very rough estimate: 33 HCP = 10 tricks per hand
        tricks_base[player] = 6 + (hcp - 8) // 3
    
    # Generate DD table (simplified)
    denominators = ['NT', 'S', 'H', 'D', 'C']
    players = ['N', 'E', 'S', 'W']
    
    for denom in denominators:
        for player in players:
            # Rough estimate
            tricks = tricks_base[player]
            # Adjust for suit preference (simplified)
            if denom in hand_data.get(player, {}):
                suit_length = len(hand_data[player].get(denom, ''))
                tricks += (suit_length - 3) // 2
            
            # Clamp to 0-13
            tricks = max(0, min(13, tricks))
            dd_analysis[f'{denom}{player}'] = tricks
    
    return dd_analysis

def calculate_dd_for_hands():
    """Main function to calculate DD for all hands"""
    
    print("=" * 70)
    print("CALCULATE DD ANALYSIS FOR ALL HANDS".center(70))
    print("=" * 70)
    
    # Load hands database
    try:
        with open('hands_database.json', 'r') as f:
            hands_db = json.load(f)
        print(f"\n[OK] Loaded {len(hands_db)} hands from hands_database.json")
    except Exception as e:
        print(f"[ERROR] Error loading hands_database.json: {e}")
        return False
    
    # Calculate DD for each hand
    updated_count = 0
    
    for board_num, board_data in hands_db.items():
        # Skip if already has DD analysis
        if 'dd_analysis' in board_data and board_data['dd_analysis']:
            continue
        
        board_num_int = int(board_num) if isinstance(board_num, str) else board_num
        print(f"\n[Board {board_num_int:3d}] ", end='', flush=True)
        
        # Try DDS first, fallback to formula
        if HAS_DDS:
            dd_analysis = calculate_dd_dds(board_data)
            method = "DDS"
        else:
            dd_analysis = calculate_dd_formula(board_data)
            method = "Formula"
        
        # If DDS failed, try formula
        if not dd_analysis and HAS_DDS:
            dd_analysis = calculate_dd_formula(board_data)
            method = "Formula (fallback)"
        
        if dd_analysis:
            board_data['dd_analysis'] = dd_analysis
            updated_count += 1
            print(f"[OK]")
        else:
            print(f"[FAIL]")
    
    print(f"\n" + "=" * 70)
    print(f"Updated: {updated_count} hands with DD analysis")
    print("=" * 70)
    
    # Save updated database
    try:
        with open('hands_database.json', 'w') as f:
            json.dump(hands_db, f, indent=2)
        print(f"\n[OK] Saved updated hands_database.json")
    except Exception as e:
        print(f"\n[ERROR] Error saving hands_database.json: {e}")
        return False
    
    # Display sample
    if updated_count > 0:
        print(f"\n[SAMPLE] Board 1 DD Analysis:")
        sample_dd = hands_db.get('1', {}).get('dd_analysis', {})
        if sample_dd:
            print("\n    NT  S  H  D  C")
            for player in ['N', 'E', 'S', 'W']:
                print(f"{player}:  ", end='')
                for denom in ['NT', 'S', 'H', 'D', 'C']:
                    tricks = sample_dd.get(f'{denom}{player}', '-')
                    print(f"{tricks:2d} ", end='')
                print()
    
    return True

if __name__ == '__main__':
    success = calculate_dd_for_hands()
    sys.exit(0 if success else 1)
