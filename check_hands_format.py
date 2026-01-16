import json

with open('app/www/hands_database.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

first_event = list(data['events'].values())[0]
first_board = first_event['boards']['1']
hands = first_board['hands']

print('ELLER VERİ KONTROLÜ')
print('=' * 50)
for pos in ['North', 'South', 'East', 'West']:
    hand = hands[pos]
    s_count = len(hand['S'])
    h_count = len(hand['H'])
    d_count = len(hand['D'])
    c_count = len(hand['C'])
    total = s_count + h_count + d_count + c_count
    
    print(f'{pos}:')
    print(f'  Spade: {hand["S"]} ({s_count})')
    print(f'  Heart: {hand["H"]} ({h_count})')
    print(f'  Diamond: {hand["D"]} ({d_count})')
    print(f'  Club: {hand["C"]} ({c_count})')
    print(f'  TOPLAM: {total} kart')
    print()

# BridgeBase format check
print('\nBRIDGEBASE FORMAT TEST')
print('=' * 50)
n_str = hand['S'] + hands['North']['H'] + hands['North']['D'] + hands['North']['C']
print(f'North format: {n_str}')
print(f'North total: {len(n_str)} (13 olmalı)')
