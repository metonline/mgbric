import json

with open('hands_database.json', 'r') as f:
    database = json.load(f)

# Find Board 10 for event 405376 on 20.01.2026
for entry in database:
    if entry.get("event_id") == "405376" and entry.get("date") == "20.01.2026" and entry.get("board") == 10:
        print("Board 10 - 20.01.2026 (dealer = East):")
        print(f"N: {entry['N']}")
        print(f"E: {entry['E']}")
        print(f"S: {entry['S']}")
        print(f"W: {entry['W']}")
        print()
        print("Expected (from vugraph):")
        print(f"N: JT9.4.AJ865.AQT9")
        print(f"E: Q64.9865.72.KJ32")
        print(f"S: 832.JT7.KQ43.874")
        print(f"W: AK75.AKQ32.T9.65")
