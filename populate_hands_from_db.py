#!/usr/bin/env python3
import json

# Load tournament data
with open('database.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Generate hands_database.json with basic structure for the UI
hands_db = []
hand_id = 1

for event_key, event_data in sorted(data['events'].items()):
    event_id = event_data.get('id')
    event_date = event_data.get('date', '')
    event_name = event_data.get('name', '')
    
    # Process NS results
    ns_results = event_data.get('results', {}).get('NS', [])
    for i, result in enumerate(ns_results, 1):
        pair1 = result.get('Oyuncu 1', f'Pair {i}')
        pair2 = result.get('Oyuncu 2', '')
        score = result.get('Skor', 0)
        
        hands_db.append({
            'id': str(hand_id),
            'board': i,
            'event_id': event_id,
            'event_name': event_name,
            'date': event_date,
            'direction': 'NS',
            'pair': f'{pair1} - {pair2}' if pair2 else pair1,
            'score': score,
            'dealer': 'N',
            'vulnerability': 'NS',
            'N': 'AKQJ.KQJ.AKQ.AKQ',
            'S': 'AKQJ.KQJ.AKQ.AKQ',
            'E': 'AKQJ.KQJ.AKQ.AKQ',
            'W': 'AKQJ.KQJ.AKQ.AKQ',
            'dd_analysis': {}
        })
        hand_id += 1
    
    # Process EW results
    ew_results = event_data.get('results', {}).get('EW', [])
    for i, result in enumerate(ew_results, 1):
        pair1 = result.get('Oyuncu 1', f'Pair {i}')
        pair2 = result.get('Oyuncu 2', '')
        score = result.get('Skor', 0)
        
        hands_db.append({
            'id': str(hand_id),
            'board': i,
            'event_id': event_id,
            'event_name': event_name,
            'date': event_date,
            'direction': 'EW',
            'pair': f'{pair1} - {pair2}' if pair2 else pair1,
            'score': score,
            'dealer': 'N',
            'vulnerability': 'EW',
            'N': 'AKQJ.KQJ.AKQ.AKQ',
            'S': 'AKQJ.KQJ.AKQ.AKQ',
            'E': 'AKQJ.KQJ.AKQ.AKQ',
            'W': 'AKQJ.KQJ.AKQ.AKQ',
            'dd_analysis': {}
        })
        hand_id += 1

# Save as hands_database.json
with open('hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(hands_db, f, ensure_ascii=False, indent=2)

# Summary
print(f"[OK] Created hands_database.json with {len(hands_db)} entries")

dates_summary = {}
for hand in hands_db:
    date = hand['date']
    dates_summary[date] = dates_summary.get(date, 0) + 1

print("\nHands by date:")
for date in sorted(dates_summary.keys()):
    count = dates_summary[date]
    print(f"  {date}: {count} hands")

print(f"\nTotal: {sum(dates_summary.values())} hands")
