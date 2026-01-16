import json

data = json.load(open('database.json', encoding='utf-8-sig'))

# Show all dates with 2025
dates_2025 = {}
for r in data:
    tarih = r.get('Tarih', 'N/A')
    if '2025' in tarih:
        if tarih not in dates_2025:
            dates_2025[tarih] = 0
        dates_2025[tarih] += 1

if dates_2025:
    print(f"✓ Bulundu 2025 tarihleri:")
    for d in sorted(dates_2025.keys(), reverse=True):
        print(f"  {d}: {dates_2025[d]} records")
else:
    print("❌ 2025 tarihleri bulunamadı")
    
    # Show all unique dates
    all_dates = set()
    for r in data:
        all_dates.add(r.get('Tarih', 'N/A'))
    
    sorted_dates = sorted(list(all_dates), reverse=True)
    print(f"\nEn son 10 tarih:")
    for d in sorted_dates[:10]:
        print(f"  {d}")
