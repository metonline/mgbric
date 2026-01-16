import json
from datetime import datetime

data = json.load(open('database.json', encoding='utf-8-sig'))

# Search for 30.12.2025 or December 2025
found = False
for r in data:
    if '30.12' in str(r.get('Tarih', '')) or ('404057' in str(r.get('Link', ''))):
        print(f"✓ Found: {r.get('Tarih')} - {r.get('Turnuva')} - {r.get('Oyuncu 1')}")
        found = True

if not found:
    print("❌ Event 404057 not found in database")
    print(f"\nTotal records: {len(data)}")
    
    # Show dates with event ID
    dates = {}
    for r in data:
        d = r.get('Tarih', 'N/A')
        if d not in dates:
            dates[d] = 0
        dates[d] += 1
    
    sorted_dates = sorted(dates.keys(), reverse=True)
    print(f"\nMost recent dates:")
    for d in sorted_dates[:10]:
        print(f"  {d}: {dates[d]} records")
