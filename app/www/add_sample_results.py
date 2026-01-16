#!/usr/bin/env python3
"""
Add sample tournament results to the database for demonstration
"""

import json
import random

# Sample pair names (Turkish bridge players)
PAIRS = [
    "Emine Billur Araz - Rabia Yeşim Somer",
    "Fikret Güneş - Nadir Ismet Hergünşer",
    "Ali Yılmaz - Mehmet Demir",
    "Ayşe Kaya - Fatima Şahin",
    "Hasan Özdemir - Kerem Aksu",
    "Sevil Çetin - Duygu Yalçın",
    "Ibrahim Turgut - Kemal Arslan",
    "Zeynep Güzel - Serpil Kartal",
    "Yaşar Kılıç - Ruşen Sever",
    "Nesrin Gökçe - Figen Uzun",
]

CONTRACTS = [
    "1N", "2N", "3N", "4N", "5N", "6N", "7N",
    "1♠", "2♠", "3♠", "4♠", "5♠", "6♠", "7♠",
    "1♥", "2♥", "3♥", "4♥", "5♥", "6♥", "7♥",
    "1♦", "2♦", "3♦", "4♦", "5♦", "6♦", "7♦",
    "1♣", "2♣", "3♣", "4♣", "5♣", "6♣", "7♣",
]

def generate_sample_results(num_pairs=10):
    """Generate sample results for demonstration"""
    results = []
    
    for i in range(num_pairs):
        pair_name = PAIRS[i % len(PAIRS)] if i < len(PAIRS) else f"Pair {i}"
        direction = "N-S" if i % 2 == 0 else "E-W"
        contract = random.choice(CONTRACTS)
        score = random.randint(0, 100)
        
        results.append({
            "pair_names": pair_name,
            "pair_num": str(i + 1),
            "direction": direction,
            "contract": contract,
            "score": score
        })
    
    # Sort by score descending
    results.sort(key=lambda x: x['score'], reverse=True)
    return results

def main():
    print("Adding sample results to hands_database.json...")
    
    # Load existing database
    with open('hands_database.json', 'r', encoding='utf-8') as f:
        database = json.load(f)
    
    # Get event
    event = database.get('events', {}).get('hosgoru_04_01_2026', {})
    boards = event.get('boards', {})
    
    total_updated = 0
    
    # Add sample results to each board
    for board_key in boards.keys():
        sample_results = generate_sample_results(num_pairs=10)
        boards[board_key]['results'] = sample_results
        total_updated += 1
    
    print(f"Updated {total_updated} boards with sample results")
    
    # Save updated database
    with open('hands_database.json', 'w', encoding='utf-8') as f:
        json.dump(database, f, ensure_ascii=False, indent=2)
    
    print("✓ Database updated successfully!")
    print(f"Each board now has 10 sample results with pair names, directions, contracts, and scores")

if __name__ == '__main__':
    main()
