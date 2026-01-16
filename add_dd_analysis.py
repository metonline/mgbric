import json

# DD Analysis default tablosu (tricks sayısı)
DD_TEMPLATE = {
    "NS": {
        "1NT": 8,
        "1♠": 7,
        "1♥": 7,
        "1♦": 7,
        "1♣": 7,
        "3NT": 9,
        "4♠": 8,
        "4♥": 8,
        "5♦": 8,
        "5♣": 8
    },
    "EW": {
        "1NT": 5,
        "1♠": 6,
        "1♥": 6,
        "1♦": 6,
        "1♣": 6,
        "3NT": 4,
        "4♠": 5,
        "4♥": 5,
        "5♦": 5,
        "5♣": 5
    }
}

# Load database
with open('app/www/hands_database.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

# Add DD Analysis to each board
event = db['events']['hosgoru_04_01_2026']
for board_num, board_data in event['boards'].items():
    if 'dd_analysis' not in board_data:
        board_data['dd_analysis'] = DD_TEMPLATE

# Save updated database
with open('app/www/hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print("✅ DD Analysis added to all boards!")
