import json

data = json.load(open(r'c:\Users\metin\Desktop\BRIC\database.json', encoding='utf-8'))
akşam = [r for r in data if r.get('Tarih') == '26.12.2025' and '20:0' in r.get('Turnuva', '')]
champs = [r for r in akşam if r.get('Sıra') == 1 or r.get('Sıra') == '1']

print(f'Akşam turnuvası toplam: {len(akşam)} kayıt')
print(f'Şampiyonlar: {len(champs)} kayıt')
print()

# NS şampiyonları
ns_champs = [c for c in champs if c.get('Direction') == 'NS']
print(f'Kuzey-Güney ({len(ns_champs)}):')
for c in ns_champs:
    print(f"  - {c.get('Oyuncu 1')} & {c.get('Oyuncu 2')} ({c.get('Skor')}%)")

# EW şampiyonları
ew_champs = [c for c in champs if c.get('Direction') == 'EW']
print(f'Doğu-Batı ({len(ew_champs)}):')
for c in ew_champs:
    print(f"  - {c.get('Oyuncu 1')} & {c.get('Oyuncu 2')} ({c.get('Skor')}%)")
