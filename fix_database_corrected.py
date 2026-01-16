import json

# Load database
with open('app/www/hands_database.json', encoding='utf-8') as f:
    db = json.load(f)

boards = db['events']['hosgoru_04_01_2026']['boards']

# Fix the 4 problematic boards
# Board 7 East: QT54.-.9874.JT942
boards['7']['hands']['East'] = {'S': 'QT54', 'H': '', 'D': '9874', 'C': 'JT942'}

# Board 9 East: AQT8.62.-.KT43
boards['9']['hands']['East'] = {'S': 'AQT8', 'H': '62', 'D': '', 'C': 'KT43'}

# Board 17 East: AKQ8.KT7.J97532.-
boards['17']['hands']['East'] = {'S': 'AKQ8', 'H': 'KT7', 'D': 'J97532', 'C': ''}

# Board 19 North: -.AQ843.63.JT9642
boards['19']['hands']['North'] = {'S': '', 'H': 'AQ843', 'D': '63', 'C': 'JT9642'}

# Verify all hands have 13 cards
print("Verifying corrected hands:")
for board_num in [7, 9, 17, 19]:
    board = boards[str(board_num)]
    print(f'\nBoard {board_num}:')
    for pos in ['North', 'East', 'South', 'West']:
        suits = board['hands'][pos]
        total = sum(len(suits[s]) for s in suits)
        hand_str = f"{suits['S']}.{suits['H']}.{suits['D']}.{suits['C']}"
        status = "✓" if total == 13 else "✗"
        print(f'  {status} {pos}: {hand_str} (total={total})')

# Save corrected database
with open('app/www/hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print("\n✓ Database corrected successfully!")
