#!/usr/bin/env python3
"""LIN formatını test et ve DD hesapla"""

from endplay.types import Deal
from endplay.dds import calc_dd_table

# LIN: md|4S3458KAH47AD57KC5,S267QH8KD49TAC78Q,S9JH3569D2368C6TA,|
# 4 = dealer West
# Sıra: South, West, North, East (boş = hesaplanacak)

# LIN formatından çözümle (kartlar küçükten büyüğe sıralı)
south = 'AK8543.A74.K75.5'   # S3458KA H47A D57K C5
west = 'Q762.K8.AT94.Q87'    # S267Q H8K D49TA C78Q  
north = 'J9.9653.8632.AT6'   # S9J H3569 D2368 C6TA

print("LIN'den çözümlenen eller:")
print(f"South: {south}")
print(f"West: {west}")
print(f"North: {north}")

# Her suit için kart say
all_cards = 'AKQJT98765432'

def count_cards(hand):
    suits = hand.split('.')
    return sum(len(s) for s in suits)

for name, hand in [('South', south), ('West', west), ('North', north)]:
    print(f'{name}: {count_cards(hand)} kart')

# East hesapla (kalan kartlar)
south_s, south_h, south_d, south_c = south.split('.')
west_s, west_h, west_d, west_c = west.split('.')
north_s, north_h, north_d, north_c = north.split('.')

east_s = ''.join(c for c in all_cards if c not in south_s + west_s + north_s)
east_h = ''.join(c for c in all_cards if c not in south_h + west_h + north_h)
east_d = ''.join(c for c in all_cards if c not in south_d + west_d + north_d)
east_c = ''.join(c for c in all_cards if c not in south_c + west_c + north_c)
east = f'{east_s}.{east_h}.{east_d}.{east_c}'
print(f'East (calc): {east} = {count_cards(east)} kart')

# PBN formatı: dealer:N E S W (saat yönünde N'den başlayarak)
pbn = f"N:{north} {east} {south} {west}"
print(f"\nPBN: {pbn}")

# DD hesapla
try:
    deal = Deal(pbn)
    table = calc_dd_table(deal)
    print(f"\nDD Sonucu: {table}")
    
    # Parse et
    parts = str(table).split(';')
    print("\n=== DD Tablosu ===")
    print("     ♣  ♦  ♥  ♠  NT")
    for part in parts[1:]:
        pos, vals = part.split(':')
        tricks = vals.split(',')
        print(f"  {pos}: {' '.join(t.rjust(2) for t in tricks)}")
        
except Exception as e:
    print(f"HATA: {e}")
