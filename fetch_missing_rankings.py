#!/usr/bin/env python3
"""
Eksik sıralama verilerini periyodik olarak çeken script.
Her 30 dakikada bir çalıştırılabilir.

Usage:
    python fetch_missing_rankings.py           # Eksik tüm verileri çek
    python fetch_missing_rankings.py --once    # Sadece bir kez çalış
    python fetch_missing_rankings.py --daemon  # Arka planda 30 dakikada bir çalış
"""

import json
import time
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from pathlib import Path
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

BOARD_RESULTS_FILE = Path(__file__).parent / "board_results.json"
HANDS_DATABASE_FILE = Path(__file__).parent / "hands_database.json"

BASE_URL = "https://clubs.vugraph.com/hosgoru"
REQUEST_TIMEOUT = 15
MAX_WORKERS = 5


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


def parse_contract(cell):
    """Kontrat hücresini parse et"""
    text = cell.get_text(strip=True)
    # Suit codes'u sembolle değiştir
    suit_map = {'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣'}
    for code, symbol in suit_map.items():
        if code in text:
            text = text.replace(code, symbol)
    return text


def get_event_info(event_id):
    """Turnuva bilgilerini ve pair isimlerini al"""
    try:
        url = f'{BASE_URL}/eventresults.php?event={event_id}'
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.encoding = 'iso-8859-9'
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # Turnuva adı
        name = ''
        h1 = soup.find('h1')
        if h1:
            name = h1.get_text(strip=True)
        
        # Pair sayısı ve isimleri
        ns_pairs = 0
        ew_pairs = 0
        ns_pair_names = {}
        ew_pair_names = {}
        
        # NS table
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    # İlk hücre pair numarası mı?
                    first_cell = cells[0].get_text(strip=True)
                    if first_cell.isdigit():
                        pair_num = int(first_cell)
                        # Link içindeki isimler
                        links = row.find_all('a')
                        names = [l.get_text(strip=True) for l in links]
                        if len(names) >= 2:
                            pair_name = f"{names[0]} - {names[1]}"
                            # NS veya EW bölümü?
                            th = table.find('th')
                            if th:
                                th_text = th.get_text(strip=True).upper()
                                if 'NS' in th_text or 'KUZEY' in th_text:
                                    ns_pair_names[pair_num] = pair_name
                                    ns_pairs = max(ns_pairs, pair_num)
                                elif 'EW' in th_text or 'DOĞU' in th_text:
                                    ew_pair_names[pair_num] = pair_name
                                    ew_pairs = max(ew_pairs, pair_num)
        
        return {
            'name': name,
            'ns_pairs': ns_pairs if ns_pairs else 10,
            'ew_pairs': ew_pairs if ew_pairs else 10,
            'ns_pair_names': ns_pair_names,
            'ew_pair_names': ew_pair_names
        }
    except Exception as e:
        print(f"    Event info error: {e}")
        return {'name': '', 'ns_pairs': 10, 'ew_pairs': 10, 'ns_pair_names': {}, 'ew_pair_names': {}}


def fetch_pair_result(event_id, board_num, pair_num, direction, pair_names_dict):
    """Bir çift için board sonucunu çeker (IMP ve MP formatlarını destekler)"""
    try:
        # Her zaman NS sayfasını kullan
        url = f'{BASE_URL}/boarddetails.php?event={event_id}&section=A&pair={pair_num}&direction=NS&board={board_num}'
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.encoding = 'iso-8859-9'
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # Page not found kontrolü
        if 'Page not Found' in resp.text or 'Sayfa Bulunamadı' in resp.text:
            return None
        
        # Pair ismini al
        pair_names = ""
        
        # NS için h3'ten dene
        if direction == 'NS':
            h3 = soup.find('h3')
            if h3:
                h3_text = h3.get_text(strip=True)
                match = re.search(r'\d{2}:\d{2}\s*\.\.\.\s*(.+?)\s*\.\.\.\s*(?:Bord|Masa)', h3_text)
                if match:
                    pair_names = match.group(1).strip()
        
        # Dict'ten al
        if not pair_names and pair_names_dict and pair_num in pair_names_dict:
            pair_names = pair_names_dict[pair_num]
        
        if not pair_names:
            pair_names = f"Pair {pair_num}"
        
        # Results tablosunu bul
        results_table = soup.find('table', class_='results')
        if not results_table:
            return None
        
        rows = results_table.find_all('tr')
        if not rows:
            return None
        
        # Format belirleme: başlık satırına bak
        header_row = rows[0].find_all(['td', 'th'])
        is_imp_format = False
        for cell in header_row:
            txt = cell.get_text(strip=True).upper()
            if 'IMP' in txt:
                is_imp_format = True
                break
        
        # Highlighted satırı bul (fantastic, resultspecial, resultsimportant)
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 6:
                cell_class = cells[0].get('class', [''])[0] if cells[0].get('class') else ''
                if cell_class not in ['fantastic', 'resultspecial', 'resultsimportant']:
                    continue
                
                if is_imp_format:
                    # IMP Format: Kontrat, Dekleran, Sonuç, Atak?, Skor, IMP
                    contract = parse_contract(cells[0])
                    declarer = cells[1].get_text(strip=True)
                    result_text = cells[2].get_text(strip=True)
                    
                    # Skor ve IMP'yi bul
                    score = ''
                    imp = 0
                    for c in cells[3:]:
                        txt = c.get_text(strip=True)
                        if txt and txt.replace('-', '').replace('.', '').isdigit():
                            if '.' in txt:
                                imp = float(txt)
                            elif not score:
                                score = txt
                    
                    if direction == 'NS':
                        return {
                            'pair_names': pair_names,
                            'direction': 'NS',
                            'contract': contract,
                            'declarer': declarer,
                            'result': result_text,
                            'lead': '',
                            'score': score,
                            'percent': imp  # IMP'de "percent" aslında IMP değeri
                        }
                    else:
                        return {
                            'pair_names': pair_names,
                            'direction': 'EW',
                            'contract': contract,
                            'declarer': declarer,
                            'result': result_text,
                            'lead': '',
                            'score': f"-{score}" if score and not score.startswith('-') else score,
                            'percent': -imp
                        }
                else:
                    # MP Format: Kontrat, Dekleran, Sonuç, Atak, SkorNS, SkorEW, %NS, %EW
                    contract = parse_contract(cells[0])
                    declarer = cells[1].get_text(strip=True)
                    result_text = cells[2].get_text(strip=True)
                    
                    if len(cells) >= 8:
                        lead = cells[3].get_text(strip=True)
                        score_ns = cells[4].get_text(strip=True)
                        score_ew = cells[5].get_text(strip=True)
                        pct_ns = cells[6].get_text(strip=True)
                        pct_ew = cells[7].get_text(strip=True)
                    else:
                        lead = ''
                        score_ns = cells[3].get_text(strip=True) if len(cells) > 3 else ''
                        score_ew = cells[4].get_text(strip=True) if len(cells) > 4 else ''
                        pct_ns = cells[5].get_text(strip=True) if len(cells) > 5 else ''
                        pct_ew = cells[6].get_text(strip=True) if len(cells) > 6 else ''
                    
                    try:
                        pct = float(pct_ns) if direction == 'NS' else float(pct_ew)
                    except:
                        pct = 0
                    
                    if direction == 'NS':
                        return {
                            'pair_names': pair_names,
                            'direction': 'NS',
                            'contract': contract,
                            'declarer': declarer,
                            'result': result_text,
                            'lead': lead,
                            'score': score_ns if score_ns else f"-{score_ew}",
                            'percent': pct
                        }
                    else:
                        return {
                            'pair_names': pair_names,
                            'direction': 'EW',
                            'contract': contract,
                            'declarer': declarer,
                            'result': result_text,
                            'lead': lead,
                            'score': score_ew if score_ew else f"-{score_ns}",
                            'percent': 100 - pct if pct else 0
                        }
        
        return None
    except Exception as e:
        return None


def fetch_board_results(event_id, board_num, ns_pairs, ew_pairs, ns_pair_names, ew_pair_names):
    """Bir board'un tüm sonuçlarını paralel olarak çeker"""
    all_results = []
    
    tasks = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # NS çiftleri
        for pair_num in range(1, ns_pairs + 1):
            tasks.append(executor.submit(
                fetch_pair_result, event_id, board_num, pair_num, 'NS', ns_pair_names
            ))
        
        # EW çiftleri
        for pair_num in range(1, ew_pairs + 1):
            tasks.append(executor.submit(
                fetch_pair_result, event_id, board_num, pair_num, 'EW', ew_pair_names
            ))
        
        for future in as_completed(tasks):
            result = future.result()
            if result:
                all_results.append(result)
    
    # Yüzdeye (veya IMP'ye) göre sırala
    all_results.sort(key=lambda x: x.get('percent', 0), reverse=True)
    for i, r in enumerate(all_results):
        r['rank'] = i + 1
    
    return all_results


def fetch_event_rankings(event_id, num_boards=30):
    """Bir event'in tüm board'larının sıralamasını çek"""
    print(f"  Event bilgileri alınıyor...")
    info = get_event_info(event_id)
    print(f"    {info['name']} - NS:{info['ns_pairs']} EW:{info['ew_pairs']}")
    
    event_results = {}
    
    for board_num in range(1, num_boards + 1):
        print(f"  Board {board_num}/{num_boards}...", end=' ', flush=True)
        results = fetch_board_results(
            event_id, board_num, 
            info['ns_pairs'], info['ew_pairs'],
            info.get('ns_pair_names', {}), info.get('ew_pair_names', {})
        )
        
        if results:
            key = f"{event_id}_{board_num}"
            event_results[key] = {
                'event_id': event_id,
                'board': board_num,
                'results': results,
                'fetched_at': datetime.now().isoformat()
            }
            print(f"{len(results)} sonuç")
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
        existing = {'boards': {}, 'events': {}, 'updated_at': ''}
    
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
