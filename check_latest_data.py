import json
from collections import defaultdict

data = json.load(open('database.json', encoding='utf-8-sig'))
print(f'Total records: {len(data)}')

# Group by date
dates = defaultdict(list)
for r in data:
    dates[r.get('Tarih', 'N/A')].append(r)

# Show last 5 dates
sorted_dates = sorted(dates.keys(), reverse=True)
print(f'\nLast 5 dates:')
for date in sorted_dates[:5]:
    print(f"  {date}: {len(dates[date])} records")

# Show all records for 30.12.2025
if '30.12.2025' in dates:
    print(f'\n30.12.2025 records ({len(dates["30.12.2025"])}):')
    for r in dates['30.12.2025']:
        print(f"  {r.get('Turnuva', '')} - {r.get('Oyuncu 1', '')} - {r.get('Skor', '')}")
else:
    print('\n❌ No records for 30.12.2025')
