import json

# Load database
with open('hands_database.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Fix event 405659 date from 01.01.2026 to 24.01.2026
for hand in data:
    if hand.get('event_id') == 405659:
        hand['date'] = '24.01.2026'

# Save back
with open('hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Verify
data = json.load(open('hands_database.json'))
e405659 = [h for h in data if h['event_id'] == 405659]
print(f'Event 405659: {len(e405659)} hands with date {e405659[0].get("date")}')
dates = sorted(set(h.get('date') for h in data))
print(f'All dates in database: {dates}')
