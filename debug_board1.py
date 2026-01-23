import json

data = json.load(open('hands_database.json'))

# Find all Board 1 entries
board_1_entries = [x for x in data if x['board'] == 1]
print(f"Total Board 1 entries: {len(board_1_entries)}\n")

for entry in board_1_entries[:3]:
    print(f"Event {entry['event_id']}, Date {entry['date']}:")
    print(f"  N: {entry['N']}\n")

# Find the specific one we're looking for
target = [x for x in data if x['event_id'] == '405376' and x['date'] == '20.01.2026' and x['board'] == 1]
if target:
    print(f"\nTarget (Event 405376, 20.01.2026, Board 1):")
    print(f"  N: {target[0]['N']}")
