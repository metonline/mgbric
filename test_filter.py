import requests
from datetime import datetime

try:
    # Get database
    r = requests.get('http://localhost:5000/get_database', timeout=5)
    data = r.json()
    print(f'✓ Database: {len(data)} records')
    
    # Filter for December 2025 (current month)
    today = datetime.now()
    start_date = datetime(today.year, today.month, 1)
    if today.month == 12:
        end_date = datetime(today.year, 12, 31)
    else:
        end_date = datetime(today.year, today.month + 1, 1)
        from datetime import timedelta
        end_date -= timedelta(days=1)
    
    def parse_date(date_str):
        day, month, year = date_str.split('.')
        return datetime(int(year), int(month), int(day))
    
    filtered = []
    for record in data:
        try:
            record_date = parse_date(record['Tarih'])
            if start_date <= record_date <= end_date and int(record['Sıra']) > 0:
                filtered.append(record)
        except:
            pass
    
    month_str = start_date.strftime("%B %Y")
    print(f'✓ Bu Ay filtresi: {len(filtered)} records in {month_str}')
    if filtered:
        s = filtered[0]
        print(f'  Sample: {s["Tarih"]}, {s["Oyuncu 1"]} vs {s["Oyuncu 2"]}, Sira={s["Sıra"]}')
        
except Exception as e:
    import traceback
    print(f'✗ Error: {e}')
    traceback.print_exc()
