import json
with open('app/www/hands_database.json', encoding='utf-8') as f:
    db = json.load(f)

boards = db['events']['hosgoru_04_01_2026']['boards']

# Check values
dealers = set()
vulns = set()

for i in range(1, 31):
    board = boards[str(i)]
    dealers.add(board.get('dealer', 'MISSING'))
    vulns.add(board.get('vulnerability', 'MISSING'))

print("Dealers found:", dealers)
print("Vulnerabilities found:", vulns)
