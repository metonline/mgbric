import json

data = json.load(open('database.json', encoding='utf-8-sig'))

# Search for records with 404057 in the link or "30-12-2025" in Turnuva field
found = False
for r in data:
    turnuva = r.get('Turnuva', '')
    link = r.get('Link', '')
    tarih = r.get('Tarih', '')
    
    if '30-12-2025' in turnuva or '404057' in link:
        print(f"✓ Bulundu:")
        print(f"  Tarih: {tarih}")
        print(f"  Turnuva: {turnuva}")
        print(f"  Oyuncu 1: {r.get('Oyuncu 1')}")
        print(f"  Link: {link}\n")
        found = True
        break

if not found:
    print("❌ 404057 veya 30-12-2025 bulunamadı")
    print("\nTurnu basında (30 ile başlayan ve 2025 içeren:")
    for r in data:
        turnuva = r.get('Turnuva', '')
        if '30' in turnuva and '2025' in turnuva:
            print(f"  Tarih: {r.get('Tarih')} -> Turnuva: {turnuva}")
            break
