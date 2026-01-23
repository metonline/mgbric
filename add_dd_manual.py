#!/usr/bin/env python3
"""
DD verisi olmayan tarihler için dd_results.json'a veri ekler
Bridgewebs API'si yerine basit bir online DD API kullanır
"""

import json
import requests
from datetime import datetime

# Bridge kurallarına göre dealer ve vulnerability
def get_dealer_for_board(board):
    """Board numarasına göre dealer döndür"""
    dealers = ['N', 'E', 'S', 'W']
    return dealers[(board - 1) % 4]

def get_vulnerability_for_board(board):
    """Board numarasına göre vulnerability döndür"""
    # Standart bridge vulnerability döngüsü (16 board)
    vuln_cycle = [
        'None', 'NS', 'EW', 'Both',  # 1-4
        'NS', 'EW', 'Both', 'None',  # 5-8
        'EW', 'Both', 'None', 'NS',  # 9-12
        'Both', 'None', 'NS', 'EW'   # 13-16
    ]
    return vuln_cycle[(board - 1) % 16]

def hand_to_pbn(n, s, e, w, dealer='N'):
    """El formatını PBN deal string'e çevir"""
    if dealer == 'N':
        return f"N:{n} {e} {s} {w}"
    elif dealer == 'E':
        return f"E:{e} {s} {w} {n}"
    elif dealer == 'S':
        return f"S:{s} {w} {n} {e}"
    elif dealer == 'W':
        return f"W:{w} {n} {e} {s}"
    return f"N:{n} {e} {s} {w}"

def calculate_dd_via_api(pbn_deal):
    """
    Online DD API kullanarak double dummy hesapla
    https://bridgewinners.com/dd/ veya benzer servisleri kullanabilir
    """
    # Şimdilik None döndür - manuel hesaplama gerekebilir
    return None

def calculate_lott(dd_result, n_hand, s_hand, e_hand, w_hand):
    """Law of Total Tricks hesapla"""
    if not dd_result:
        return None
    
    suit_symbols = {'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣'}
    
    def count_suit(hand, suit_index):
        parts = hand.split('.')
        if suit_index < len(parts):
            return len(parts[suit_index]) if parts[suit_index] != '-' else 0
        return 0
    
    ns_fits = {}
    ew_fits = {}
    
    for suit_idx, suit in enumerate(['S', 'H', 'D', 'C']):
        ns_len = count_suit(n_hand, suit_idx) + count_suit(s_hand, suit_idx)
        ew_len = count_suit(e_hand, suit_idx) + count_suit(w_hand, suit_idx)
        ns_tricks = max(dd_result.get('N', {}).get(suit, 0), dd_result.get('S', {}).get(suit, 0))
        ew_tricks = max(dd_result.get('E', {}).get(suit, 0), dd_result.get('W', {}).get(suit, 0))
        ns_fits[suit] = {'length': ns_len, 'tricks': ns_tricks}
        ew_fits[suit] = {'length': ew_len, 'tricks': ew_tricks}
    
    best_ns = max(ns_fits.items(), key=lambda x: (x[1]['length'], x[1]['tricks']))
    best_ew = max(ew_fits.items(), key=lambda x: (x[1]['length'], x[1]['tricks']))
    total_tricks = best_ns[1]['tricks'] + best_ew[1]['tricks']
    
    return {
        'total_tricks': total_tricks,
        'ns_fit': {
            'suit': suit_symbols[best_ns[0]],
            'suit_code': best_ns[0],
            'length': best_ns[1]['length'],
            'tricks': best_ns[1]['tricks']
        },
        'ew_fit': {
            'suit': suit_symbols[best_ew[0]],
            'suit_code': best_ew[0],
            'length': best_ew[1]['length'],
            'tricks': best_ew[1]['tricks']
        }
    }

def main():
    # 1. Hangi tarihler eksik kontrol et
    with open('double_dummy/dd_results.json', 'r', encoding='utf-8') as f:
        dd_data = json.load(f)
    
    dd_dates = set(h['date'] for h in dd_data)
    print(f"DD mevcut tarihler: {sorted(dd_dates)}")
    
    # 2. hands_database.json'dan tüm tarihleri al
    with open('hands_database.json', 'r', encoding='utf-8') as f:
        hands = json.load(f)
    
    hands_dates = set(h.get('Tarih', '') for h in hands)
    print(f"hands_database tarihleri: {sorted(hands_dates)}")
    
    # 3. Eksik tarihleri bul
    missing_dates = hands_dates - dd_dates
    print(f"\nEksik tarihler: {sorted(missing_dates)}")
    
    if not missing_dates:
        print("Tüm tarihler için DD verisi mevcut!")
        return
    
    # 4. Eksik her tarih için placeholder veri oluştur
    new_entries = []
    max_id = max(h.get('id', 0) for h in dd_data) + 1
    
    for date in sorted(missing_dates):
        date_hands = [h for h in hands if h.get('Tarih') == date]
        print(f"\n{date}: {len(date_hands)} el için veri hazırlanıyor...")
        
        for hand in date_hands:
            board = hand.get('Board', 1)
            dealer = get_dealer_for_board(board)
            vuln = get_vulnerability_for_board(board)
            
            n = hand.get('N', '')
            s = hand.get('S', '')
            e = hand.get('E', '')
            w = hand.get('W', '')
            
            entry = {
                'id': max_id,
                'board': board,
                'date': date,
                'dealer': dealer,
                'vulnerability': vuln,
                'N': n,
                'S': s,
                'E': e,
                'W': w,
                'dd_result': None,  # DD hesaplanacak
                'optimum': None,
                'lott': None
            }
            
            new_entries.append(entry)
            max_id += 1
            print(f"  Board {board}: {n[:10]}... Dealer:{dealer} Vuln:{vuln}")
    
    # 5. Yeni verileri ekle ve kaydet
    dd_data.extend(new_entries)
    
    with open('double_dummy/dd_results.json', 'w', encoding='utf-8') as f:
        json.dump(dd_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ {len(new_entries)} yeni el dd_results.json'a eklendi")
    print("NOT: DD verileri henüz hesaplanmadı (null). Bridgewebs veya başka bir servis kullanarak hesaplanmalı.")

if __name__ == '__main__':
    main()
