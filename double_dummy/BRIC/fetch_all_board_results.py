"""
Tüm turnuvaların board sonuçlarını çekip board_results.json'a kaydeder.
Bu script bir kez çalıştırılır, sonra veriler local'de kullanılır.
"""

import json
import requests
from bs4 import BeautifulSoup
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import time
import os

# Ayarlar
OUTPUT_FILE = 'board_results.json'
MAX_WORKERS = 10  # Paralel istek sayısı
REQUEST_TIMEOUT = 15

def parse_contract_cell(cell):
    """Kontrat hücresini parse et"""
    text = cell.get_text(strip=True)
    imgs = cell.find_all('img')
    for img in imgs:
        alt = img.get('alt', '')
        if alt == 'S':
            text = text.replace('', '♠')
        elif alt == 'H':
            text = text.replace('', '♥')
        elif alt == 'D':
            text = text.replace('', '♦')
        elif alt == 'C':
            text = text.replace('', '♣')
    # Sayı + suit + X/XX
    suit_map = {'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣'}
    for code, symbol in suit_map.items():
        if code in text:
            text = text.replace(code, symbol)
    return text

def parse_lead_cell(cell):
    """Atak hücresini parse et"""
    text = cell.get_text(strip=True)
    imgs = cell.find_all('img')
    suit_map = {'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣'}
    for img in imgs:
        alt = img.get('alt', '')
        if alt in suit_map:
            text = text.replace(alt, suit_map[alt])
    # Harf kodlarını da değiştir
    for code, symbol in suit_map.items():
        if code in text:
            text = text.replace(code, symbol)
    return text

def fetch_pair_result(event_id, board_num, pair_num, direction, section='A'):
    """Bir çift için board sonucunu çeker"""
    try:
        url = f'https://clubs.vugraph.com/hosgoru/boarddetails.php?event={event_id}&section={section}&pair={pair_num}&direction={direction}&board={board_num}'
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.encoding = 'iso-8859-9'
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # h3'ten isim al
        pair_names = ""
        h3 = soup.find('h3')
        if h3:
            h3_text = h3.get_text(strip=True)
            match = re.search(r'\d{2}:\d{2}\s*\.\.\.\s*(.+?)\s*\.\.\.\s*Bord', h3_text)
            if match:
                pair_names = match.group(1).strip()
        
        if not pair_names:
            return None
        
        # Highlighted satırı bul
        results_table = soup.find('table', class_='results')
        if not results_table:
            return None
        
        for row in results_table.find_all('tr'):
            cells = row.find_all('td')
            # 8 hücreli (normal) veya 7 hücreli (TBF SIMULTANE - atak yok) formatları destekle
            if len(cells) >= 7:
                cell_class = cells[0].get('class', [''])[0] if cells[0].get('class') else ''
                if cell_class in ['fantastic', 'resultspecial', 'resultsimportant']:
                    contract = parse_contract_cell(cells[0])
                    declarer = cells[1].get_text(strip=True)
                    result_text = cells[2].get_text(strip=True)
                    
                    # 8 hücre: Kontrat, Dekleran, Sonuç, Atak, SkorNS, SkorEW, %NS, %EW
                    # 7 hücre: Kontrat, Dekleran, Sonuç, SkorNS, SkorEW, %NS, %EW (atak yok)
                    if len(cells) >= 8:
                        lead = parse_lead_cell(cells[3])
                        score_ns = cells[4].get_text(strip=True) if not cells[4].find('img') else ''
                        score_ew = cells[5].get_text(strip=True) if not cells[5].find('img') else ''
                        pct_ns = cells[6].get_text(strip=True) if not cells[6].find('img') else ''
                        pct_ew = cells[7].get_text(strip=True) if not cells[7].find('img') else ''
                    else:
                        lead = ''
                        score_ns = cells[3].get_text(strip=True) if not cells[3].find('img') else ''
                        score_ew = cells[4].get_text(strip=True) if not cells[4].find('img') else ''
                        pct_ns = cells[5].get_text(strip=True) if not cells[5].find('img') else ''
                        pct_ew = cells[6].get_text(strip=True) if not cells[6].find('img') else ''
                    
                    if direction == 'NS' and score_ns:
                        return {
                            'pair_names': pair_names,
                            'direction': 'NS',
                            'contract': contract,
                            'declarer': declarer,
                            'result': result_text,
                            'lead': lead,
                            'score': score_ns,
                            'percent': float(pct_ns) if pct_ns else 0
                        }
                    elif direction == 'EW' and score_ew:
                        return {
                            'pair_names': pair_names,
                            'direction': 'EW',
                            'contract': contract,
                            'declarer': declarer,
                            'result': result_text,
                            'lead': lead,
                            'score': score_ew,
                            'percent': float(pct_ew) if pct_ew else 0
                        }
        return None
    except Exception as e:
        return None

def get_event_info(event_id):
    """Turnuva bilgilerini ve çift sayısını al"""
    try:
        url = f'https://clubs.vugraph.com/hosgoru/eventresults.php?event={event_id}'
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.encoding = 'iso-8859-9'
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # Turnuva adı ve tarihi
        tournament_name = ""
        tournament_date = ""
        h3 = soup.find('h3')
        if h3:
            h3_text = h3.get_text(strip=True)
            date_match = re.search(r'(\d{2})-(\d{2})-(\d{4})', h3_text)
            if date_match:
                day, month, year = date_match.groups()
                tournament_date = f"{day}.{month}.{year}"
            parts = h3_text.split()
            if parts:
                tournament_name = parts[0]
        
        # NS ve EW çift sayısını bul
        ns_count = 0
        ew_count = 0
        tables = soup.find_all('table')
        for table in tables:
            prev = table.find_previous(['h4', 'h3', 'h2'])
            if prev:
                prev_text = prev.get_text(strip=True)
                rows = table.find_all('tr')
                data_rows = [r for r in rows if r.find('td') and len(r.find_all('td')) >= 2]
                if 'Kuzey' in prev_text or 'North' in prev_text:
                    ns_count = len(data_rows)
                elif 'Doğu' in prev_text or 'East' in prev_text:
                    ew_count = len(data_rows)
        
        if ns_count == 0:
            ns_count = 13
        if ew_count == 0:
            ew_count = 13
            
        return {
            'name': tournament_name,
            'date': tournament_date,
            'ns_pairs': ns_count,
            'ew_pairs': ew_count
        }
    except Exception as e:
        return {'name': '', 'date': '', 'ns_pairs': 13, 'ew_pairs': 13}

def fetch_board_results(event_id, board_num, ns_count, ew_count):
    """Bir board için tüm sonuçları çeker (paralel)"""
    all_results = []
    tasks = []
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # NS çiftleri
        for pair_num in range(1, ns_count + 1):
            tasks.append(executor.submit(fetch_pair_result, event_id, board_num, pair_num, 'NS'))
        # EW çiftleri
        for pair_num in range(1, ew_count + 1):
            tasks.append(executor.submit(fetch_pair_result, event_id, board_num, pair_num, 'EW'))
        
        for future in as_completed(tasks):
            result = future.result()
            if result:
                all_results.append(result)
    
    # Yüzdeye göre sırala
    all_results.sort(key=lambda x: x['percent'], reverse=True)
    for i, r in enumerate(all_results):
        r['rank'] = i + 1
    
    return all_results

def main():
    # hands_database.json'dan event listesini al
    with open('hands_database.json', 'r', encoding='utf-8') as f:
        hands = json.load(f)
    
    # Event ve board'ları grupla
    events = {}
    for h in hands:
        event_id = h.get('event_id', '')
        board_num = h.get('Board', 0)
        date = h.get('Tarih', '')
        if event_id and board_num:
            if event_id not in events:
                events[event_id] = {'date': date, 'boards': set()}
            events[event_id]['boards'].add(board_num)
    
    print(f"Toplam {len(events)} turnuva, {sum(len(e['boards']) for e in events.values())} board bulundu.")
    
    # Mevcut veriyi yükle (devam etmek için)
    existing_data = {}
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            print(f"Mevcut veri yüklendi: {len(existing_data.get('boards', {}))} board")
        except:
            existing_data = {}
    
    # Sonuç yapısı
    result_data = existing_data if existing_data else {
        'version': '1.0',
        'last_updated': '',
        'events': {},
        'boards': {}
    }
    
    total_boards = sum(len(e['boards']) for e in events.values())
    processed = 0
    skipped = 0
    
    # Her event için
    for event_id, event_info in sorted(events.items(), key=lambda x: x[1]['date']):
        print(f"\n{'='*60}")
        print(f"Event {event_id} - {event_info['date']}")
        
        # Event bilgilerini çek
        if event_id not in result_data['events']:
            info = get_event_info(event_id)
            result_data['events'][event_id] = info
            print(f"  {info['name']} - NS:{info['ns_pairs']} EW:{info['ew_pairs']}")
        else:
            info = result_data['events'][event_id]
        
        # Her board için
        for board_num in sorted(event_info['boards']):
            board_key = f"{event_id}_{board_num}"
            
            # Zaten varsa atla
            if board_key in result_data['boards']:
                skipped += 1
                processed += 1
                continue
            
            print(f"  Board {board_num}...", end=' ', flush=True)
            start = time.time()
            
            results = fetch_board_results(event_id, board_num, info['ns_pairs'], info['ew_pairs'])
            
            result_data['boards'][board_key] = {
                'event_id': event_id,
                'board': board_num,
                'date': event_info['date'],
                'results': results
            }
            
            elapsed = time.time() - start
            processed += 1
            print(f"{len(results)} sonuç ({elapsed:.1f}s) [{processed}/{total_boards}]")
            
            # Her 10 board'da kaydet
            if processed % 10 == 0:
                result_data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                    json.dump(result_data, f, ensure_ascii=False, indent=2)
                print(f"  [Kaydedildi: {len(result_data['boards'])} board]")
    
    # Son kayıt
    result_data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Tamamlandı! {len(result_data['boards'])} board kaydedildi.")
    print(f"Atlanan (mevcut): {skipped}")
    print(f"Dosya: {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
