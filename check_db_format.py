#!/usr/bin/env python3
import json

with open('database.json', encoding='utf-8') as f:
    data = json.load(f)

if data.get('events'):
    first_event_key = list(data['events'].keys())[0]
    event = data['events'][first_event_key]
    print(f'Event: {first_event_key}')
    
    ns = event.get('results', {}).get('NS', [])
    ew = event.get('results', {}).get('EW', [])
    
    print(f'NS records: {len(ns)}')
    print(f'EW records: {len(ew)}')
    
    if ns:
        print(f'\nFirst NS record:')
        print(json.dumps(ns[0], indent=2, ensure_ascii=False))
