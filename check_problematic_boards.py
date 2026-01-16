import json

with open('app/www/hands_database.json', encoding='utf-8') as f:
    db = json.load(f)

boards = db['events']['hosgoru_04_01_2026']['boards']

# Check the problematic boards
for board_num in [7, 9, 17, 19]:
    board = boards[str(board_num)]
    print(f'\nBoard {board_num}:')
    for pos in ['North', 'East', 'South', 'West']:
        suits = board['hands'][pos]
        total = sum(len(suits[s]) for s in suits)
        hand_str = f"{suits['S']}.{suits['H']}.{suits['D']}.{suits['C']}"
        print(f'  {pos}: {hand_str} (total={total})')
