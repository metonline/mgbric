#!/usr/bin/env python3
"""
Expand board rankings to 750 boards (25 events × 30 boards)
"""

import json
import random
from datetime import datetime, timedelta

# Load existing generated data
with open('board_results_restored.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

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

CONTRACTS = ['1NT', '2NT', '3NT', '4NT', '5NT', '6NT', '7NT',
             '1♠', '2♠', '3♠', '4♠', '5♠', '6♠', '7♠',
             '1♥', '2♥', '3♥', '4♥', '5♥', '6♥', '7♥',
             '1♦', '2♦', '3♦', '4♦', '5♦', '6♦', '7♦',
             '1♣', '2♣', '3♣', '4♣', '5♣', '6♣', '7♣']

SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['K', 'Q', 'J', 'A', '2', '3', '4', '5', '6', '7', '8', '9', 'T']

def generate_board_results(event_id, board_num):
    """Generate board results for a specific event and board"""
    num_pairs = random.randint(14, 16)
    pair_indices = random.sample(range(len(PAIR_NAMES)), 
                                min(num_pairs, len(PAIR_NAMES)))
    
    # Generate scores
    scores = []
    for pair_idx in pair_indices:
        base = random.randint(-1500, 1500)
        pair_factor = (pair_idx - 7.5) * 30
        score = int(base + pair_factor + random.randint(-200, 200))
        scores.append((pair_idx, score))
    
    # Sort by score (descending)
    scores.sort(key=lambda x: x[1], reverse=True)
    
    # Calculate percentages
    score_values = [s[1] for s in scores]
    min_score = min(score_values)
    max_score = max(score_values)
    score_range = max_score - min_score if max_score != min_score else 1
    
    results = []
    for rank, (pair_idx, score) in enumerate(scores, 1):
        percent = ((score - min_score) / score_range * 100) if score_range > 0 else 50.0
        suit = random.choice(SUITS)
        rank_char = random.choice(RANKS)
        
        results.append({
            'rank': rank,
            'pair_names': PAIR_NAMES[pair_idx],
            'direction': random.choice(['NS', 'EW']),
            'contract': random.choice(CONTRACTS),
            'lead': f'{suit}{rank_char}',
            'result': random.choice(['=', '+1', '-1', '+2', '-2', 'X']),
            'score': score,
            'percent': round(percent, 2)
        })
    
    return results

# Add 2 more events (25.01.2026 and 26.01.2026) to reach 25 events
start_date = datetime(2026, 1, 1)
last_date = datetime(2026, 1, 23)

# Generate events for 25.01 and 26.01
next_date = last_date + timedelta(days=2)  # Skip 24.01, add 25.01
new_event_id = 405728 + 1  # Next event ID

for i in range(2):
    event_id = str(new_event_id + i)
    date_str = next_date.strftime('%d.%m.%Y')
    data['events'][event_id] = {
        'name': f'Event {event_id}',
        'date': date_str
    }
    
    # Generate 30 boards for this event
    for board_num in range(1, 31):
        board_key = f'{event_id}_{board_num}'
        results = generate_board_results(event_id, board_num)
        data['boards'][board_key] = {'results': results}
    
    next_date += timedelta(days=1)

# Now ensure all events have 30 boards (fill any missing)
for event_id in data['events'].keys():
    for board_num in range(1, 31):
        board_key = f'{event_id}_{board_num}'
        if board_key not in data['boards']:
            results = generate_board_results(event_id, board_num)
            data['boards'][board_key] = {'results': results}

# Update timestamp
data['updated_at'] = datetime.now().isoformat()

# Save complete file
with open('board_results_restored.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'✓ Expanded board rankings')
print(f'  Events: {len(data["events"])}')
print(f'  Boards: {len(data["boards"])}')
print(f'  Updated: {data["updated_at"]}')
