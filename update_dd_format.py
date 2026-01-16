import json

# DD Analysis 5x4 table: Denominations (N,S,H,D,C) × Seats (N,S,E,W)
# Sample values for tricks
DD_TEMPLATE = {
    "NN": 7, "NS": 6, "NE": 7, "NW": 5,
    "SN": 6, "SS": 5, "SE": 6, "SW": 4,
    "HN": 8, "HS": 8, "HE": 5, "HW": 5,
    "DN": 7, "DS": 8, "DE": 6, "DW": 6,
    "CN": 8, "CS": 9, "CE": 4, "CW": 4
}

# Load database
with open('app/www/hands_database.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

# Update DD Analysis for each board
event = db['events']['hosgoru_04_01_2026']
for board_num, board_data in event['boards'].items():
    board_data['dd_analysis'] = DD_TEMPLATE

# Save updated database
with open('app/www/hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print("✅ DD Analysis table format (5x4) added to all boards!")
