import json

with open('double_dummy/dd_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Toplam el: {len(data)}")

# LoTT verisi olmayan eller
no_lott = [h for h in data if not h.get('lott')]
print(f"LoTT verisi yok: {len(no_lott)}")
for h in no_lott[:10]:
    print(f"  Board {h.get('board')}, Tarih: {h.get('date')}")

# LoTT total_tricks olmayan eller
no_total = [h for h in data if h.get('lott') and not h.get('lott', {}).get('total_tricks')]
print(f"\nLoTT var ama total_tricks yok: {len(no_total)}")
for h in no_total[:10]:
    print(f"  Board {h.get('board')}, Tarih: {h.get('date')}, LoTT: {h.get('lott')}")

# Board numaralarını kontrol et
boards = [h.get('board') for h in data]
print(f"\nBoard aralığı: {min(boards)} - {max(boards)}")
print(f"Farklı board sayısı: {len(set(boards))}")

# Tarihlere göre grupla
dates = {}
for h in data:
    d = h.get('date', 'unknown')
    if d not in dates:
        dates[d] = []
    dates[d].append(h.get('board'))

print(f"\nTarihlere göre dağılım:")
for d, boards_list in sorted(dates.items()):
    print(f"  {d}: {len(boards_list)} el (Boardlar: {min(boards_list)}-{max(boards_list)})")
