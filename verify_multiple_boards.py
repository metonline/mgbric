import json

data = json.load(open('hands_database.json'))

# Check boards 1, 5, 10, 20, 30 from event 405376 on 20.01.2026
boards_to_check = [1, 5, 10, 20, 30]

print("Verification of boards from event 405376 on 20.01.2026:\n")

for board_num in boards_to_check:
    hand = [x for x in data if x['event_id']=='405376' and x['date']=='20.01.2026' and x['board']==board_num]
    if hand:
        h = hand[0]
        print(f"Board {board_num}:")
        print(f"  N: {h['N']}")
        print(f"  E: {h['E']}")
        print(f"  S: {h['S']}")
        print(f"  W: {h['W']}")
        print()
