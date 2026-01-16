import json

try:
    db = json.load(open('app/www/hands_database.json', encoding='utf-8'))
    event = db['events']['hosgoru_04_01_2026']
    boards = event['boards']
    print(f'✅ Database OK - {len(boards)} boards loaded')
    
    b1 = boards['1']
    print(f'Board 1 dealer: {b1["dealer"]}')
    print(f'Board 1 hands:')
    for player in ['North', 'South', 'East', 'West']:
        hand = b1['hands'][player]
        s = hand.get('S', '')
        print(f'  {player}: S{s}...')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
