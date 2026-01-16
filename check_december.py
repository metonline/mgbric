import json

data = json.load(open('database.json', encoding='utf-8-sig'))

# Find December 2025 records (any day)
dec_2025 = {}
for r in data:
    tarih = r.get('Tarih', '')
    if '12.2025' in tarih or '2025' in tarih and '12.' in tarih:
        day = tarih.split('.')[0] if tarih else 'N/A'
        if day not in dec_2025:
            dec_2025[day] = 0
        dec_2025[day] += 1

if dec_2025:
    print("Aralık 2025 (12.2025):")
    for day in sorted(dec_2025.keys()):
        print(f"  {day}.12.2025: {dec_2025[day]} records")

# Also check raw dates
all_dates = set()
for r in data:
    tarih = r.get('Tarih', '')
    if tarih and '30' in tarih and '2025' in tarih:
        all_dates.add(tarih)

if all_dates:
    print(f"\n30. gün + 2025 içeren tarihler:")
    for d in sorted(all_dates):
        print(f"  {d}")
