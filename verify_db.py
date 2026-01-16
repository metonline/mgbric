#!/usr/bin/env python3
import json

with open('app/www/hands_database.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

print('✅ Database loaded successfully')
event_key = 'hosgoru_04_01_2026'
boards = db['events'][event_key]['boards']
print(f'   Event: {event_key}')
print(f'   Boards: {len(boards)}')

b1 = boards['1']
print(f'\n✅ Board 1:')
print(f'   Dealer: {b1["dealer"]}')
print(f'   Vulnerability: {b1["vulnerability"]}')

for player in ['North', 'South', 'East', 'West']:
    hand = b1['hands'][player]
    # Count cards
    total_cards = sum(len(hand.get(s, '')) for s in ['S', 'H', 'D', 'C'])
    suits = ' '.join([f'{s}{hand.get(s, "")}' for s in ['S', 'H', 'D', 'C']])
    print(f'   {player:6}: {suits} ({total_cards} cards)')
