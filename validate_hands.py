import json
with open('app/www/hands_database.json', 'r') as f:
    data = json.load(f)
print('OK - JSON valid')
print('Events:', len(data.get('events', {})))
dates = set()
for e in data.get('events', {}).values():
    dates.add(e.get('date'))
print('Dates:', sorted(list(dates)))
