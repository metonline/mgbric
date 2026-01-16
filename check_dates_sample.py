import json

data = json.load(open('database.json', encoding='utf-8-sig'))
print('Toplam kayıt:', len(data))
print('\nİlk 5 kayıt:')
for d in data[:5]:
    print(f"  Tarih: {d.get('Tarih', 'N/A')} - Oyuncu 1: {d.get('Oyuncu 1', 'N/A')}")

print('\nSon 5 kayıt:')
for d in data[-5:]:
    print(f"  Tarih: {d.get('Tarih', 'N/A')} - Oyuncu 1: {d.get('Oyuncu 1', 'N/A')}")

# Tarih formatını kontrol et
dates = [d.get('Tarih') for d in data if d.get('Tarih')]
print(f'\nUnique tarih sayısı: {len(set(dates))}')
print(f'Min tarih: {min(dates)}')
print(f'Max tarih: {max(dates)}')
