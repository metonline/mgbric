#!/usr/bin/env python3
"""
Generate realistic board_results.json from hands_database.json
Creates plausible pair rankings for each board based on typical bridge scoring
"""

import json
import random
from pathlib import Path
from collections import defaultdict
from datetime import datetime

class BoardRankingsGenerator:
    """Generate board_results.json from hands_database.json"""
    
    PAIR_NAMES = [
        "AYŞE KUTLAY - MÜJDAT SAĞLAM",
        "HACI KANTARCI - YAŞAR KARATOPRAK",
        "METIN ÇETIN - ZEYNEP ARSLAN",
        "GÜLEN GENÇ - SERDAR YILMAZ",
        "FATMA TURAN - ALI ASLAN",
        "NİLÜFER ÇETIN - MEHMET KAYA",
        "AYLIN YILDIRIM - BURAK ÖZKAN",
        "CENGIZ AKMAN - TÜRKAN AKMAN",
        "SERAP KAPLAN - ERCAN ÖZDEMIR",
        "FULYA ARSLAN - MUSTAFA GÜZEL",
        "ECEM TOKGÖZ - ALPER YAMAN",
        "DİDEM KARA - CEM BAYRAKTAR",
        "EMINE KALKAN - HASAN GÜNER",
        "GÜLTEN DOGAN - İLKER GÜZEL",
        "ZEYNEP ÇIFTCI - DAVUT KÖSE",
    ]
    
    def __init__(self):
        self.boards_data = self._load_hands_database()
    
    def _load_hands_database(self):
        """Load and group hands by event and board"""
        try:
            with open('hands_database.json', 'r', encoding='utf-8') as f:
                hands = json.load(f)
        except FileNotFoundError:
            return defaultdict(lambda: defaultdict(list))
        
        boards_data = defaultdict(lambda: defaultdict(list))
        for hand in hands:
            event_id = str(hand.get('event_id', ''))
            board_num = hand.get('board', 0)
            if event_id and board_num:
                boards_data[event_id][board_num].append(hand)
        
        return boards_data
    
    @staticmethod
    def generate_score(board_num):
        """Generate realistic bridge scores for a board"""
        base_score = random.randint(-1500, 1500)
        return base_score

    @staticmethod
    def generate_contract():
        """Generate realistic contracts"""
        contracts = ['3NT', '4♠', '4♥', '5♦', '5♣', '1NT', '2♠', '3♣', '2♥', '6NT', '7NT', '3♣', '4♦']
        return random.choice(contracts)
    
    def generate_all(self) -> bool:
        """Generate board_results.json from hands_database.json
        
        Returns True if successful, False otherwise
        """
        try:
            output = {
                'boards': {},
                'events': {},
                'updated_at': datetime.now().isoformat()
            }
            
            # Process all events in the database
            for event_id, event_boards in sorted(self.boards_data.items()):
                output['events'][event_id] = {
                    'name': f'Event {event_id}',
                    'date': datetime.now().strftime('%d.%m.%Y')
                }
                
                # Generate data for EACH board in the event
                for board_num in sorted(event_boards.keys()):
                    board_key = f"{event_id}_{board_num}"
                    
                    # Generate 14-16 pairs for this board
                    num_pairs = random.randint(14, 16)
                    results = []
                    
                    # Create random pair results with realistic percentages
                    pair_indices = random.sample(range(len(self.PAIR_NAMES)), 
                                                min(num_pairs, len(self.PAIR_NAMES)))
                    scores = []
                    
                    for pair_idx in pair_indices:
                        score = self.generate_score(board_num)
                        scores.append(score)
                    
                    # Calculate percentages based on scores
                    min_score = min(scores)
                    max_score = max(scores)
                    score_range = max_score - min_score if max_score != min_score else 1
                    
                    for rank, pair_idx in enumerate(sorted(pair_indices, 
                                                          key=lambda i: scores[pair_indices.index(i)], 
                                                          reverse=True), 1):
                        score = scores[pair_indices.index(pair_idx)]
                        # Calculate percentage (0-100)
                        percent = ((score - min_score) / score_range * 100) if score_range > 0 else 50.0
                        
                        # Randomly assign direction for realistic data
                        direction = random.choice(['NS', 'EW'])
                        
                        results.append({
                            'rank': rank,
                            'pair_names': self.PAIR_NAMES[pair_idx],
                            'direction': direction,
                            'contract': self.generate_contract(),
                            'lead': random.choice(['♠K', '♥Q', '♦A', '♣J', '♠2', '♥3', '♦4', '♣5']),
                            'result': random.choice(['=', '+1', '-1', '+2', '-2', 'X']),
                            'score': score,
                            'percent': round(percent, 2)
                        })
                    
                    output['boards'][board_key] = {'results': results}
            
            # Save to file
            with open('board_results.json', 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            
            print(f"✓ Generated board_results.json")
            print(f"  Events: {len(output['events'])}")
            print(f"  Boards: {len(output['boards'])}")
            
            return True
            
        except Exception as e:
            print(f"✗ Error generating board_results.json: {e}")
            return False


# CLI interface - run as script
if __name__ == '__main__':
    generator = BoardRankingsGenerator()
    success = generator.generate_all()
    exit(0 if success else 1)

