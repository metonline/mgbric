import json

data = json.load(open('database.json', encoding='utf-8-sig'))

# Find all 30.12.2025 records
records_30_12 = [r for r in data if r.get('Tarih') == '30.12.2025']

print(f"✓ 30.12.2025 kayıtları: {len(records_30_12)} adet\n")

if records_30_12:
    # Show first 5
    print("İlk 5 kayıt:")
    for i, r in enumerate(records_30_12[:5], 1):
        print(f"{i}. {r.get('Turnuva')} - {r.get('Oyuncu 1')} - {r.get('Oyuncu 2')} - {r.get('Skor')}")
