#!/usr/bin/env python3
"""
Eksik sıralama verilerini periyodik olarak çeken script.
Her 30 dakikada bir çalıştırılabilir.

Usage:
    python fetch_missing_rankings.py           # Eksik tüm verileri çek
    python fetch_missing_rankings.py --once    # Sadece bir kez çalış
    python fetch_missing_rankings.py --daemon  # Arka planda 30 dakikada bir çalış
    
NOT: Bu script vugraph_utils.py modülünü kullanır.
     Ortak fonksiyonlar orada tanımlıdır (DRY prensibi).
"""

import json
import time
from datetime import datetime
from pathlib import Path
import argparse
import sys

# Ortak modül - TÜM vugraph fonksiyonları için tek kaynak
# NOT: get_event_info ve fetch_pair_result fonksiyonları artık vugraph_utils.py'den geliyor
# Bu, kod duplikasyonunu önler ve tek kaynak (DRY) prensibiyle çalışır

from vugraph_utils import (
    get_event_info, 
    fetch_pair_result,
    fetch_board_all_results,
    BASE_URL,
    REQUEST_TIMEOUT
)

BOARD_RESULTS_FILE = Path(__file__).parent / "board_results.json"
HANDS_DATABASE_FILE = Path(__file__).parent / "hands_database.json"


def get_missing_events():
    """hands_database'de olup board_results'ta olmayan event'leri bul"""
    try:
        with open(HANDS_DATABASE_FILE, 'r', encoding='utf-8') as f:
            hands = json.load(f)
        with open(BOARD_RESULTS_FILE, 'r', encoding='utf-8') as f:
            results = json.load(f)
    except Exception as e:
        print(f"[HATA] Dosya okunamadı: {e}")
        return []
    
    hands_events = set(str(x.get('event_id')) for x in hands)
    results_events = set(k.split('_')[0] for k in results.get('boards', {}).keys())
    
    missing = sorted(hands_events - results_events)
    return missing


def fetch_event_rankings(event_id, num_boards=30):
    """Bir event'in tüm board'larının sıralamasını çek - pair bazlı"""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    print(f"  Event bilgileri alınıyor...")
    info = get_event_info(event_id)
    print(f"    {info['name']} - NS:{info['ns_pairs']} EW:{info['ew_pairs']}")
    
    ns_pairs = info.get('ns_pairs', 0)
    ew_pairs = info.get('ew_pairs', 0)
    ns_pair_names = info.get('ns_pair_names', {})
    ew_pair_names = info.get('ew_pair_names', {})
    
    event_results = {}
    
    for board_num in range(1, num_boards + 1):
        print(f"  Board {board_num}/{num_boards}...", end=' ', flush=True)
        
        all_results = []
        
        # NS sonuçları - paralel (NS pair'leri için NS direction)
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {}
            for pair_num in range(1, ns_pairs + 1):
                f = executor.submit(fetch_pair_result, event_id, board_num, pair_num, 'NS', 'A', ns_pair_names)
                futures[f] = ('NS', pair_num)
            
            for future in as_completed(futures):
                result = future.result()
                if result:
                    all_results.append(result)
        
        # EW sonuçları için: NS sayfasından EW skorlarını al
        # Her NS pair'inin karşısında oturan EW pair'inin skoru tabloda var
        # Ama hangi EW pair olduğunu bilemiyoruz...
        # Çözüm: fetch_board_all_results'tan NS ve EW sonuçlarını al, 
        # pair_names'i event info'dan eşleştir
        
        if all_results:
            # fetch_board_all_results'tan EW sonuçlarını da al
            all_board_results = fetch_board_all_results(event_id, board_num)
            
            # EW sonuçlarını ekle (pair_names olmadan)
            ew_from_board = [r for r in all_board_results if r.get('direction') == 'EW']
            
            # EW pair isimlerini sırayla eşleştir (en iyi tahmin)
            ew_pair_list = list(ew_pair_names.values())
            for i, r in enumerate(ew_from_board):
                if i < len(ew_pair_list):
                    r['pair_names'] = ew_pair_list[i]
                else:
                    r['pair_names'] = f"EW Pair {i+1}"
                all_results.append(r)
            
            # Tüm sonuçları yüzdeye göre sırala (NS+EW birlikte)
            all_results.sort(key=lambda x: x.get('percent', 0), reverse=True)
            
            for i, r in enumerate(all_results):
                r['rank'] = i + 1
            
            key = f"{event_id}_{board_num}"
            event_results[key] = {
                'event_id': event_id,
                'board': board_num,
                'results': all_results,
                'fetched_at': datetime.now().isoformat()
            }
            print(f"{len(all_results)} sonuç")
        else:
            print("veri yok")
        
        time.sleep(0.1)  # Rate limiting
    
    return event_results, info


def save_results(new_boards, event_info=None, event_id=None):
    """Yeni verileri board_results.json'a ekle"""
    try:
        with open(BOARD_RESULTS_FILE, 'r', encoding='utf-8') as f:
            existing = json.load(f)
    except:
        existing = {}
    
    # Eski format kontrolü
    if 'boards' not in existing:
        existing = {'boards': existing, 'events': {}, 'updated_at': ''}
    
    existing['boards'].update(new_boards)
    
    if event_info and event_id:
        existing['events'][event_id] = {
            'name': event_info.get('name', ''),
            'ns_pairs': event_info.get('ns_pairs', 0),
            'ew_pairs': event_info.get('ew_pairs', 0)
        }
    
    existing['updated_at'] = datetime.now().isoformat()
    
    with open(BOARD_RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] {len(new_boards)} board kaydedildi")


def run_fetch():
    """Eksik verileri çek"""
    missing = get_missing_events()
    
    if not missing:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Eksik veri yok ✓")
        return 0
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Eksik event'ler: {missing}")
    
    total_fetched = 0
    for event_id in missing:
        print(f"\n[FETCH] Event {event_id}...")
        results, info = fetch_event_rankings(event_id, num_boards=30)
        
        if results:
            save_results(results, info, event_id)
            total_fetched += len(results)
            print(f"  ✓ Event {event_id}: {len(results)} board")
        else:
            print(f"  ✗ Event {event_id}: Veri alınamadı")
    
    return total_fetched


def main():
    parser = argparse.ArgumentParser(description='Eksik sıralama verilerini çek')
    parser.add_argument('--once', action='store_true', help='Sadece bir kez çalış')
    parser.add_argument('--daemon', action='store_true', help='30 dakikada bir çalış')
    parser.add_argument('--interval', type=int, default=30, help='Dakika cinsinden aralık (varsayılan: 30)')
    args = parser.parse_args()
    
    print("=" * 50)
    print("BRIC Eksik Sıralama Verisi Çekici")
    print("=" * 50)
    
    if args.daemon:
        print(f"Daemon modu: Her {args.interval} dakikada bir çalışacak")
        while True:
            try:
                run_fetch()
                print(f"\nSonraki çalışma: {args.interval} dakika sonra")
                time.sleep(args.interval * 60)
            except KeyboardInterrupt:
                print("\nDurduruldu.")
                sys.exit(0)
    else:
        count = run_fetch()
        if count > 0:
            print(f"\n✓ Toplam {count} board verisi çekildi")
        return 0


if __name__ == "__main__":
    main()
