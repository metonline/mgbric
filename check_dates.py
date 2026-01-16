import json

with open('database.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'Total records: {len(data)}')
print(f'First record date: {data[0]["Tarih"]}')
print(f'Last record date: {data[-1]["Tarih"]}')

# Find latest date
dates = []
for record in data:
    date_str = record.get('Tarih', '')
    if date_str:
        parts = date_str.split('.')
        if len(parts) == 3:
            day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            comparable = year * 10000 + month * 100 + day
            dates.append((comparable, date_str))

dates.sort(reverse=True)
print(f'\nLatest date in database: {dates[0][1]}')
print(f'Oldest date in database: {dates[-1][1]}')
