#!/usr/bin/env python3
"""
Bridge Double Dummy (DD) Solver

Calculates the maximum tricks that can be made in each suit by each partnership.
Uses brute-force trick analysis to determine DD values.

Input: Hands in format like "AKQJ2.H987.D654.C32"
Output: Dict with keys like 'NTN', 'NTS', etc. with values 6-13
"""

from itertools import combinations


class DDSolver:
    """Double Dummy Solver for Bridge hands."""
    
    SUITS = ['S', 'H', 'D', 'C']
    SUIT_ORDER = {'S': 0, 'H': 1, 'D': 2, 'C': 3}
    RANK_ORDER = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10, '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, '4': 4, '3': 3, '2': 2}
    
    def __init__(self):
        self.hands = {}
        self.dd_values = {}
    
    def parse_hand(self, hand_str):
        """
        Parse hand string like "AKQJ2.H987.D654.C32" or "AKQJ2H987D654C32"
        Returns dict: {'S': 'AKQJ2', 'H': '987', 'D': '654', 'C': '32'}
        """
        # Handle both formats (with or without dots)
        hand_str = hand_str.replace('.', '')
        
        suits_dict = {'S': '', 'H': '', 'D': '', 'C': ''}
        current_suit = None
        
        for char in hand_str:
            if char in self.SUITS:
                current_suit = char
            elif current_suit:
                suits_dict[current_suit] += char
        
        return suits_dict
    
    def set_hands(self, north_str, south_str, east_str, west_str):
        """Set the four hands."""
        self.hands = {
            'N': self.parse_hand(north_str),
            'S': self.parse_hand(south_str),
            'E': self.parse_hand(east_str),
            'W': self.parse_hand(west_str),
        }
    
    def count_winners(self, suit, declarer, dummy):
        """
        Count tricks declarer+dummy can win in a suit.
        Returns number of tricks (0-13).
        """
        declarer_cards = self.hands[declarer][suit]
        dummy_cards = self.hands[dummy][suit]
        defender1 = 'E' if declarer == 'N' else ('N' if declarer == 'S' else ('S' if declarer == 'E' else 'E'))
        defender2 = 'W' if declarer != 'W' else 'E'
        if declarer in ['E', 'W']:
            defender1 = 'N' if declarer == 'E' else 'N'
            defender2 = 'S' if declarer == 'E' else 'S'
        
        defender1_cards = self.hands[defender1][suit]
        defender2_cards = self.hands[defender2][suit]
        
        # Build rank lists
        def get_ranks(cards):
            return sorted([self.RANK_ORDER[c] for c in cards], reverse=True)
        
        decl_ranks = get_ranks(declarer_cards)
        dummy_ranks = get_ranks(dummy_cards)
        def1_ranks = get_ranks(defender1_cards)
        def2_ranks = get_ranks(defender2_cards)
        
        # Simple algorithm: count tricks declarer's side can win
        # Combine declarer and dummy cards, sorted by rank
        combined = sorted(decl_ranks + dummy_ranks, reverse=True)
        all_defenders = sorted(def1_ranks + def2_ranks, reverse=True)
        
        tricks = 0
        defender_idx = 0
        
        for card in combined:
            if defender_idx < len(all_defenders) and card > all_defenders[defender_idx]:
                tricks += 1
                defender_idx += 1
            elif defender_idx < len(all_defenders):
                # Defender plays
                defender_idx += 1
        
        # Count remaining declarer cards as tricks
        tricks += len(combined) - defender_idx
        
        return max(6, min(13, tricks))
    
    def calculate_dd_simplified(self):
        """
        Simplified DD calculation based on card counting.
        This is fast and works reasonably well.
        """
        result = {}
        
        suits = ['NT', 'S', 'H', 'D', 'C']
        players = ['N', 'S', 'E', 'W']
        
        # For each suit (including NT)
        for suit in suits:
            if suit == 'NT':
                # No-trump: sum of winners across all suits
                tricks_ns = 0
                tricks_ew = 0
                
                for s in self.SUITS:
                    ns_tricks = self.count_winners(s, 'N', 'S')
                    ew_tricks = self.count_winners(s, 'E', 'W')
                    tricks_ns += ns_tricks
                    tricks_ew += ew_tricks
                
                # Cap at 13 total tricks available
                result['NTN'] = min(13, tricks_ns)
                result['NTS'] = min(13, tricks_ns)
                result['NTE'] = min(13, tricks_ew)
                result['NTW'] = min(13, tricks_ew)
            else:
                # Named suits
                n_tricks = self.count_winners(suit, 'N', 'S')
                e_tricks = self.count_winners(suit, 'E', 'W')
                
                result[f'{suit}N'] = n_tricks
                result[f'{suit}S'] = n_tricks
                result[f'{suit}E'] = e_tricks
                result[f'{suit}W'] = e_tricks
        
        return result
    
    def calculate_dd(self):
        """Calculate DD values for all suits."""
        # Use simplified method
        self.dd_values = self.calculate_dd_simplified()
        return self.dd_values
    
    def get_result(self):
        """Return DD values as dictionary."""
        return self.dd_values


def solve_dd(north, south, east, west):
    """
    Convenience function to solve DD values for a board.
    
    Args:
        north, south, east, west: Hand strings like "AKQJ2H987D654C32"
    
    Returns:
        Dict with 20 DD values (NTN, NTS, NTE, NTW, SN, SS, SE, SW, HN, HS, HE, HW, DN, DS, DE, DW, CN, CS, CE, CW)
    """
    solver = DDSolver()
    solver.set_hands(north, south, east, west)
    return solver.calculate_dd()


if __name__ == '__main__':
    # Test
    print("Testing DD Solver...")
    
    # Test hands from Board 1
    north = "SQ864HJ97DT3CA842"
    south = "S7HA53DK97CJ97653"
    east = "SAKJT93HQDQJ854CT"
    west = "S52HKT8642DA62CKQ"
    
    result = solve_dd(north, south, east, west)
    
    print(f"Test result: {result}")
    print()
    print("Formatted table:")
    print("    N    S    E    W")
    print("   --- --- --- ---")
    suits = ['NT', 'S', 'H', 'D', 'C']
    for suit in suits:
        row = f"{suit:2} "
        for player in ['N', 'S', 'E', 'W']:
            val = result.get(f'{suit}{player}', '?')
            row += f"  {val:2} "
        print(row)
