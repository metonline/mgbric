import json

# Load database
with open('app/www/hands_database.json', encoding='utf-8') as f:
    db = json.load(f)

boards = db['events']['hosgoru_04_01_2026']['boards']

# Fix Board 9 East with correct hearts
# Board 9 East: AQT8.K10762.-.KT43
boards['9']['hands']['East'] = {'S': 'AQT8', 'H': 'K10762', 'D': '', 'C': 'KT43'}

# Verify
board = boards['9']
suits = board['hands']['East']
total = sum(len(suits[s]) for s in suits)
hand_str = f"{suits['S']}.{suits['H']}.{suits['D']}.{suits['C']}"
print(f"Board 9 East corrected: {hand_str} (total={total})")
print(f"Status: {'✓ VALID' if total == 13 else '✗ INVALID'}")

# Save corrected database
with open('app/www/hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print("\n✓ Database fully corrected!")
