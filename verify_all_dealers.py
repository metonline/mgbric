import json

with open('hands_database.json', 'r') as f:
    database = json.load(f)

# Check boards representing each dealer position
test_boards = [
    (1, "N"),   # dealer N
    (2, "E"),   # dealer E
    (3, "S"),   # dealer S
    (4, "W"),   # dealer W
    (5, "N"),   # dealer N (cycle repeats)
]

for board_num, expected_dealer in test_boards:
    for entry in database:
        if entry.get("event_id") == "405376" and entry.get("date") == "20.01.2026" and entry.get("board") == board_num:
            print(f"Board {board_num} (dealer = {expected_dealer}):")
            print(f"  N: {entry['N']}")
            print(f"  E: {entry['E']}")
            print(f"  S: {entry['S']}")
            print(f"  W: {entry['W']}")
            print()
