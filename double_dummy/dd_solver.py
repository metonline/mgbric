#!/usr/bin/env python3
"""
Double Dummy Solver - endplay kütüphanesi ile DD analizi yapar

Kullanım:
    python dd_solver.py                    # Tüm elleri analiz et
    python dd_solver.py --date 17.01.2026  # Belirli tarih
    python dd_solver.py --board 1          # Belirli board
    python dd_solver.py --limit 30         # İlk 30 eli analiz et
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

try:
    from endplay.types import Deal, Player, Vul
    from endplay.dds import calc_dd_table, par
    ENDPLAY_AVAILABLE = True
except ImportError:
    print("HATA: endplay kütüphanesi bulunamadı!")
    print("Kurulum: pip install endplay")
    ENDPLAY_AVAILABLE = False

# Dosya yolları
HANDS_DB_PATH = Path(__file__).parent.parent / "hands_database.json"
DD_RESULTS_PATH = Path(__file__).parent / "dd_results.json"

def normalize_hand(hand_str):
    """
    El stringindeki '-' karakterlerini '' (boş) ile değiştir
    '-' void (renkte kart yok) anlamına gelir
    Input: "AKQ.-.JT98.A7632" -> "AKQ..JT98.A7632"
    """
    if not hand_str:
        return hand_str
    # Her suit'i ayrı işle
    suits = hand_str.split('.')
    normalized = []
    for suit in suits:
        if suit == '-':
            normalized.append('')  # Void = empty string
        else:
            normalized.append(suit)
    return '.'.join(normalized)

def hand_to_pbn(n, s, e, w, dealer='N'):
    """
    El formatını PBN deal string'e çevir
    Input: "T9752.9732.J72.3" (S.H.D.C formatında)
    Output: PBN deal string
    
    PBN formatı: dealer'dan başlayarak saat yönünde 4 el
    N dealer: N E S W
    E dealer: E S W N
    S dealer: S W N E
    W dealer: W N E S
    
    NOT: '-' karakteri void (renkte kart yok) anlamına gelir
    """
    # Normalize hands: convert '-' to '' for voids
    n = normalize_hand(n)
    s = normalize_hand(s)
    e = normalize_hand(e)
    w = normalize_hand(w)
    
    if dealer == 'N':
        return f"N:{n} {e} {s} {w}"
    elif dealer == 'E':
        return f"E:{e} {s} {w} {n}"
    elif dealer == 'S':
        return f"S:{s} {w} {n} {e}"
    elif dealer == 'W':
        return f"W:{w} {n} {e} {s}"
    else:
        # Default N
        return f"N:{n} {e} {s} {w}"

def parse_dd_table(table):
    """
    endplay DD table'ı dict formatına çevir
    Input: "♣,♦,♥,♠,NT;N:3,6,3,5,4;E:10,6,10,8,9;S:3,6,3,5,4;W:10,6,9,8,9"
    Output: {N: {C:3, D:6, H:3, S:5, NT:4}, ...}
    """
    result = {}
    
    # Table string'i parse et
    table_str = str(table)
    parts = table_str.split(';')
    
    # İlk kısım sütun başlıkları: ♣,♦,♥,♠,NT
    suits_order = ['C', 'D', 'H', 'S', 'NT']
    
    # Her pozisyon için
    for part in parts[1:]:  # İlk kısmı (başlıkları) atla
        if ':' in part:
            pos, values = part.split(':')
            tricks = values.split(',')
            result[pos] = {}
            for i, suit in enumerate(suits_order):
                if i < len(tricks):
                    result[pos][suit] = int(tricks[i])
    
    return result

def get_vul_enum(vuln_str):
    """Vulnerability string'i Vul enum'a çevir"""
    vuln_map = {
        'None': Vul.none,
        'NS': Vul.ns,
        'EW': Vul.ew,
        'Both': Vul.both,
        'All': Vul.both,
        'none': Vul.none,
        'ns': Vul.ns,
        'ew': Vul.ew,
        'both': Vul.both,
        'all': Vul.both,
        '-': Vul.none,
        'Yok': Vul.none,
    }
    return vuln_map.get(vuln_str, Vul.none)

def get_dealer_enum(dealer_str):
    """Dealer string'i Player enum'a çevir"""
    dealer_map = {
        'N': Player.north,
        'E': Player.east,
        'S': Player.south,
        'W': Player.west,
    }
    return dealer_map.get(dealer_str, Player.north)

def calculate_lott(dd_result, n_hand, s_hand, e_hand, w_hand):
    """
    Law of Total Tricks hesapla
    LoTT = NS'in en iyi fit'indeki el sayısı + EW'nin en iyi fit'indeki el sayısı
    
    Returns: {
        'total_tricks': 17,
        'ns_fit': {'suit': '♠', 'length': 9, 'tricks': 9},
        'ew_fit': {'suit': '♣', 'length': 8, 'tricks': 8}
    }
    """
    if not dd_result:
        return None
    
    suit_symbols = {'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣'}
    
    def count_suit(hand, suit_index):
        """El stringinden belirli rengin kartlarını say"""
        parts = hand.split('.')
        if suit_index < len(parts):
            suit = parts[suit_index]
            # '-' veya '' void demektir = 0 kart
            if suit == '-' or suit == '':
                return 0
            return len(suit)
        return 0
    
    # Her renk için fit uzunluklarını hesapla (0=S, 1=H, 2=D, 3=C)
    ns_fits = {}
    ew_fits = {}
    
    for suit_idx, suit in enumerate(['S', 'H', 'D', 'C']):
        ns_len = count_suit(n_hand, suit_idx) + count_suit(s_hand, suit_idx)
        ew_len = count_suit(e_hand, suit_idx) + count_suit(w_hand, suit_idx)
        
        # NS için en iyi tricks (N veya S'den yüksek olanı)
        ns_tricks = max(dd_result.get('N', {}).get(suit, 0), dd_result.get('S', {}).get(suit, 0))
        ew_tricks = max(dd_result.get('E', {}).get(suit, 0), dd_result.get('W', {}).get(suit, 0))
        
        ns_fits[suit] = {'length': ns_len, 'tricks': ns_tricks}
        ew_fits[suit] = {'length': ew_len, 'tricks': ew_tricks}
    
    # En uzun fit'i bul (aynı uzunlukta ise en yüksek trick olanı)
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

def format_optimum(par_result):
    """
    Par sonucunu 'EW 5♥; -450' formatında döndür
    """
    if not par_result or par_result.score == 0:
        return {'text': 'Pass Out', 'score': 0, 'declarer': None, 'contract': None}
    
    # İlk kontratı al
    contract = None
    for c in par_result:
        contract = c
        break
    
    if not contract:
        return {'text': f'Score: {par_result.score}', 'score': par_result.score, 'declarer': None, 'contract': None}
    
    # Contract string'i parse et: "4♥E+1" -> level=4, denom=♥, declarer=E, overtricks=+1
    contract_str = str(contract)  # "4♥E+1"
    
    # Declarer (E/W = EW, N/S = NS)
    if 'N' in contract_str or 'S' in contract_str:
        side = 'NS'
    else:
        side = 'EW'
    
    # Level (ilk rakam)
    level = contract.level
    
    # Denom symbol
    denom_symbols = {'♣': '♣', '♦': '♦', '♥': '♥', '♠': '♠', 'N': 'NT'}
    denom_symbol = '?'
    for sym in denom_symbols:
        if sym in contract_str:
            denom_symbol = denom_symbols[sym]
            break
    
    # Overtricks (+1, +2, etc.)
    overtricks = 0
    if '+' in contract_str:
        try:
            overtricks = int(contract_str.split('+')[1])
        except:
            pass
    
    # Toplam el sayısı
    total_tricks = level + 6 + overtricks
    
    # Format: "EW 5♥; -450"
    score = par_result.score
    text = f"{side} {total_tricks}{denom_symbol}; {score:+d}"
    
    return {
        'text': text,
        'score': score,
        'declarer': side,
        'contract': f"{total_tricks}{denom_symbol}",
        'level': level,
        'denom': denom_symbol,
        'tricks': total_tricks
    }

def calculate_dd_for_hand(hand_data):
    """
    Tek bir el için DD, optimum skor ve LoTT hesapla
    Returns: (dd_table, optimum, lott) tuple
    """
    # Handle nested 'hands' structure
    hands = hand_data.get('hands', hand_data)
    n = hands.get('N', '')
    s = hands.get('S', '')
    e = hands.get('E', '')
    w = hands.get('W', '')
    dealer = hand_data.get('dealer', 'N')
    vuln = hand_data.get('vulnerability', 'None')
    
    if not all([n, s, e, w]):
        return None, None, None
    
    try:
        # PBN deal oluştur
        pbn = hand_to_pbn(n, s, e, w, dealer)
        
        # Deal objesi oluştur
        deal = Deal(pbn)
        
        # DD table hesapla
        table = calc_dd_table(deal)
        
        # Par score hesapla
        vul_enum = get_vul_enum(vuln)
        dealer_enum = get_dealer_enum(dealer)
        par_result = par(table, vul_enum, dealer_enum)
        
        # Optimum formatla
        optimum = format_optimum(par_result)
        
        # Dict formatına çevir
        dd_result = parse_dd_table(table)
        
        # LoTT hesapla
        lott = calculate_lott(dd_result, n, s, e, w)
        
        return dd_result, optimum, lott
        
    except Exception as e:
        print(f"    DD hesaplama hatası: {e}")
        return None, None, None

def load_hands_database():
    """hands_database.json yükle"""
    if not HANDS_DB_PATH.exists():
        print(f"HATA: {HANDS_DB_PATH} bulunamadı!")
        return []
    
    with open(HANDS_DB_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_dd_results(results):
    """DD sonuçlarını kaydet"""
    with open(DD_RESULTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"✅ Sonuçlar kaydedildi: {DD_RESULTS_PATH}")

def update_hands_database(hands, results_map):
    """
    hands_database.json'daki dd_analysis, optimum ve lott alanlarını güncelle
    """
    updated_count = 0
    for hand in hands:
        # KEY: Use event_id + board (not date, since multiple events can be on same date)
        key = f"{hand.get('event_id')}_{hand.get('board')}"
        if key in results_map:
            hand['dd_analysis'] = results_map[key]['dd']
            hand['optimum'] = results_map[key]['optimum']
            hand['lott'] = results_map[key]['lott']
            updated_count += 1
    
    # Kaydet
    with open(HANDS_DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(hands, f, indent=2, ensure_ascii=False)
    
    print(f"✅ hands_database.json güncellendi: {updated_count} el")

def format_dd_table_ascii(dd_result):
    """DD tablosunu ASCII formatında göster"""
    if not dd_result:
        return "DD verisi yok"
    
    suits = ['C', 'D', 'H', 'S', 'NT']
    positions = ['N', 'S', 'E', 'W']
    
    # Başlık
    header = "     ♣  ♦  ♥  ♠  NT"
    lines = [header, "-" * len(header)]
    
    for pos in positions:
        if pos in dd_result:
            values = [str(dd_result[pos].get(s, '-')).rjust(2) for s in suits]
            lines.append(f"  {pos}  {' '.join(values)}")
    
    return '\n'.join(lines)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Double Dummy Solver')
    parser.add_argument('--date', help='Belirli tarih (DD.MM.YYYY)')
    parser.add_argument('--board', type=int, help='Belirli board numarası')
    parser.add_argument('--limit', type=int, help='Maksimum el sayısı')
    parser.add_argument('--update-db', action='store_true', help='hands_database.json\'u güncelle')
    parser.add_argument('--verbose', '-v', action='store_true', help='Detaylı çıktı')
    args = parser.parse_args()
    
    if not ENDPLAY_AVAILABLE:
        sys.exit(1)
    
    print("=" * 60)
    print("🃏 Double Dummy Solver")
    print("=" * 60)
    print()
    
    # Veritabanını yükle
    hands = load_hands_database()
    print(f"📂 {len(hands)} el yüklendi")
    
    # Filtreleme
    filtered_hands = hands.copy()
    
    # Varsayılan olarak DD analizi OLMAyan elleri işle
    filtered_hands = [h for h in filtered_hands if 'dd_analysis' not in h]
    if filtered_hands:
        print(f"⚡ DD analizi olmayan elleri işleniyor: {len(filtered_hands)} el")
    
    if args.date:
        filtered_hands = [h for h in filtered_hands if h.get('date') == args.date]
        print(f"📅 {args.date} tarihli {len(filtered_hands)} el filtrelendi")
    
    if args.board:
        filtered_hands = [h for h in filtered_hands if h.get('board') == args.board]
        print(f"🎯 Board {args.board}: {len(filtered_hands)} el filtrelendi")
    
    # Limit uygula
    if args.limit:
        filtered_hands = filtered_hands[:args.limit]
        print(f"🔢 Limit: {len(filtered_hands)} el")
    
    print()
    print(f"{'='*60}")
    print(f"📊 {len(filtered_hands)} el işlenecek")
    print(f"{'='*60}")
    print()
    
    # Her el için DD hesapla
    results = []
    results_map = {}  # date_board -> dd_result
    success_count = 0
    
    start_time = datetime.now()
    
    for i, hand in enumerate(filtered_hands):
        board_num = hand.get('board', i+1)
        date = hand.get('date', 'Unknown')
        event_id = hand.get('event_id', 'unknown')
        
        print(f"[{i+1}/{len(filtered_hands)}] Board {board_num} ({date})...", end=' ')
        
        # DD hesapla
        dd_result, optimum, lott = calculate_dd_for_hand(hand)
        
        if dd_result:
            print("✅", end='')
            if optimum:
                print(f" {optimum['text']}", end='')
            if lott:
                print(f" | LoTT: {lott['total_tricks']}", end='')
            print()
            success_count += 1
            
            # Sonuç kaydet
            result_entry = {
                'id': hand.get('id'),
                'board': board_num,
                'date': date,
                'dealer': hand.get('dealer'),
                'vulnerability': hand.get('vulnerability'),
                'N': hand.get('N'),
                'S': hand.get('S'),
                'E': hand.get('E'),
                'W': hand.get('W'),
                'dd_result': dd_result,
                'optimum': optimum,
                'lott': lott
            }
            results.append(result_entry)
            
            # Map'e ekle (dd_result, optimum ve lott birlikte)
            # KEY: Use event_id + board (not date, since multiple events can be on same date)
            key = f"{event_id}_{board_num}"
            results_map[key] = {'dd': dd_result, 'optimum': optimum, 'lott': lott}
            
            # Verbose modda tabloyu göster
            if args.verbose:
                print(format_dd_table_ascii(dd_result))
                print()
        else:
            print("❌")
    
    elapsed = (datetime.now() - start_time).total_seconds()
    
    # Sonuçları kaydet
    if results:
        save_dd_results(results)
    
    # hands_database.json'u güncelle
    if args.update_db and results_map:
        update_hands_database(hands, results_map)
    
    print()
    print("=" * 60)
    print(f"✅ Tamamlandı: {success_count}/{len(filtered_hands)} el ({elapsed:.1f} saniye)")
    print("=" * 60)
    
    if not args.update_db:
        print()
        print("💡 hands_database.json'u güncellemek için: --update-db")

if __name__ == "__main__":
    main()
