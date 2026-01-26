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
                    
                    # Generate 7-8 tables (each table has 1 NS pair and 1 EW pair)
                    num_tables = random.randint(7, 8)
                    
                    # Shuffle pair names and split into NS and EW
                    shuffled_pairs = random.sample(self.PAIR_NAMES, min(num_tables * 2, len(self.PAIR_NAMES)))
                    ns_pairs = shuffled_pairs[:num_tables]
                    ew_pairs = shuffled_pairs[num_tables:num_tables*2]
                    
                    # Generate table results - each table has one NS score (EW gets negative)
                    table_results = []
                    for i in range(min(len(ns_pairs), len(ew_pairs))):
                        ns_score = self.generate_score(board_num)
                        contract = self.generate_contract()
                        lead = random.choice(['♠K', '♥Q', '♦A', '♣J', '♠2', '♥3', '♦4', '♣5', '♦T', '♥6', '♠8', '♣5'])
                        result = random.choice(['=', '+1', '-1', '+2', '-2'])
                        
                        table_results.append({
                            'ns_pair': ns_pairs[i],
                            'ew_pair': ew_pairs[i],
                            'ns_score': ns_score,
                            'contract': contract,
                            'lead': lead,
                            'result': result
                        })
                    
                    # Calculate matchpoints for NS pairs (compared to other NS scores)
                    ns_scores = [t['ns_score'] for t in table_results]
                    
                    results = []
                    
                    # Process NS pairs
                    for i, table in enumerate(table_results):
                        # Matchpoints: 2 points for each pair you beat, 1 for each tie
                        matchpoints = 0
                        for j, other_score in enumerate(ns_scores):
                            if i != j:
                                if table['ns_score'] > other_score:
                                    matchpoints += 2
                                elif table['ns_score'] == other_score:
                                    matchpoints += 1
                        
                        max_matchpoints = (len(ns_scores) - 1) * 2
                        percent = (matchpoints / max_matchpoints * 100) if max_matchpoints > 0 else 50.0
                        
                        results.append({
                            'pair_names': table['ns_pair'],
                            'direction': 'NS',
                            'contract': table['contract'],
                            'lead': table['lead'],
                            'result': table['result'],
                            'score': table['ns_score'],
                            'percent': round(percent, 2)
                        })
                    
                    # Process EW pairs (their matchpoints are inverse - they want NS to score low)
                    for i, table in enumerate(table_results):
                        ew_score = -table['ns_score']  # EW score is negative of NS
                        
                        matchpoints = 0
                        for j, other_ns_score in enumerate(ns_scores):
                            if i != j:
                                other_ew_score = -other_ns_score
                                if ew_score > other_ew_score:
                                    matchpoints += 2
                                elif ew_score == other_ew_score:
                                    matchpoints += 1
                        
                        max_matchpoints = (len(ns_scores) - 1) * 2
                        percent = (matchpoints / max_matchpoints * 100) if max_matchpoints > 0 else 50.0
                        
                        results.append({
                            'pair_names': table['ew_pair'],
                            'direction': 'EW',
                            'contract': table['contract'],
                            'lead': table['lead'],
                            'result': table['result'],
                            'score': ew_score,
                            'percent': round(percent, 2)
                        })
                    
                    # Sort by percent descending and assign ranks
                    results.sort(key=lambda x: x['percent'], reverse=True)
                    for rank, r in enumerate(results, 1):
                        r['rank'] = rank
                    
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

