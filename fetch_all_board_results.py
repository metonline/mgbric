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

# IMP turnuvaları - bunlar % bazlı değil, ayrı işlenecek
IMP_EVENTS = ['405080', '405171', '405248', '405321']

# NOT: NO_DATA_EVENTS listesi kaldırıldı - artık dinamik kontrol yapılıyor
# Eğer vugraph'ta veri yoksa, bir sonraki çalışmada tekrar denenecek

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

def fetch_pair_result(event_id, board_num, pair_num, direction, section='A', pair_names_dict=None):
    """Bir çift için board sonucunu çeker"""
    try:
        # Her zaman NS sayfasını kullan (EW sayfaları çalışmıyor)
        url = f'https://clubs.vugraph.com/hosgoru/boarddetails.php?event={event_id}&section={section}&pair={pair_num}&direction=NS&board={board_num}'
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.encoding = 'iso-8859-9'
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # Page not found kontrolü
        if 'Page not Found' in resp.text or 'Sayfa Bulunamadı' in resp.text:
            return None
        
        # Pair ismini al
        pair_names = ""
        
        # Önce h3'ten dene (NS için)
        if direction == 'NS':
            h3 = soup.find('h3')
            if h3:
                h3_text = h3.get_text(strip=True)
                match = re.search(r'\d{2}:\d{2}\s*\.\.\.\s*(.+?)\s*\.\.\.\s*Bord', h3_text)
                if match:
                    pair_names = match.group(1).strip()
        
        # h3'te bulunamazsa veya EW ise dict'ten al
        if not pair_names and pair_names_dict and pair_num in pair_names_dict:
            pair_names = pair_names_dict[pair_num]
        
        if not pair_names:
            return None
        
        # Highlighted satırı bul
        results_table = soup.find('table', class_='results')
        if not results_table:
            return None
        
        rows = results_table.find_all('tr')
        if not rows:
            return None
        
        # Format belirleme: ilk satırın ilk hücresine bak
        first_row_cells = rows[0].find_all('td')
        first_header = first_row_cells[0].get_text(strip=True) if first_row_cells else ''
        
        # IMP Format: "Atak" ile başlar, kontrat bilgisi yok
        if first_header == 'Atak':
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 3:
                    cell_class = cells[0].get('class', [''])[0] if cells[0].get('class') else ''
                    if cell_class in ['fantastic', 'resultspecial', 'resultsimportant']:
                        # IMP format: Atak yok, sadece skor ve IMP var
                        # Hücreler: (boş), SkorNS, (boş), IMP, (boş) veya benzeri
                        score_ns = ''
                        score_ew = ''
                        imp = ''
                        
                        for c in cells:
                            txt = c.get_text(strip=True)
                            if txt and txt.replace('.','').replace('-','').isdigit():
                                if '.' in txt:
                                    imp = txt
                                elif not score_ns and not score_ew:
                                    # İlk sayı skor
                                    score_ns = txt
                        
                        if score_ns:
                            if direction == 'NS':
                                return {
                                    'pair_names': pair_names,
                                    'direction': 'NS',
                                    'contract': '-',
                                    'declarer': '-',
                                    'result': '-',
                                    'lead': '-',
                                    'score': score_ns,
                                    'percent': float(imp) if imp else 0
                                }
                            elif direction == 'EW':
                                return {
                                    'pair_names': pair_names,
                                    'direction': 'EW',
                                    'contract': '-',
                                    'declarer': '-',
                                    'result': '-',
                                    'lead': '-',
                                    'score': f"-{score_ns}" if score_ns else '',
                                    'percent': -float(imp) if imp else 0
                                }
            return None
        
        # MP Format: "Kontrat" ile başlar veya ilk highlighted satırda kontrat var
        for row in rows:
            cells = row.find_all('td')
            # 8 hücreli (normal) veya 7 hücreli (TBF SIMULTANE - atak yok) formatları destekle
            if len(cells) >= 7:
                cell_class = cells[0].get('class', [''])[0] if cells[0].get('class') else ''
                if cell_class in ['fantastic', 'resultspecial', 'resultsimportant']:
                    contract = parse_contract_cell(cells[0])
                    # Kontrat yoksa (örn: -6, geç oynandı) atla
                    if not contract or contract in ['-6', '-', '']:
                        return None
                    
                    declarer = cells[1].get_text(strip=True)
                    result_text = cells[2].get_text(strip=True)
                    
                    # 8 hücre: Kontrat, Dekleran, Sonuç, Atak, SkorNS, SkorEW, %NS, %EW
                    # 7 hücre: Kontrat, Dekleran, Sonuç, SkorNS, SkorEW, %NS, %EW (atak yok)
                    if len(cells) >= 8:
                        lead = parse_lead_cell(cells[3])
                        score_ns = cells[4].get_text(strip=True) if not cells[4].find('img') else ''
                        score_ew = cells[5].get_text(strip=True) if not cells[5].find('img') else ''
                        pct_ns_str = cells[6].get_text(strip=True) if not cells[6].find('img') else ''
                        pct_ew_str = cells[7].get_text(strip=True) if not cells[7].find('img') else ''
                    else:
                        lead = ''
                        score_ns = cells[3].get_text(strip=True) if not cells[3].find('img') else ''
                        score_ew = cells[4].get_text(strip=True) if not cells[4].find('img') else ''
                        pct_ns_str = cells[5].get_text(strip=True) if not cells[5].find('img') else ''
                        pct_ew_str = cells[6].get_text(strip=True) if not cells[6].find('img') else ''
                    
                    # Yüzdeleri parse et
                    pct_ns = float(pct_ns_str) if pct_ns_str else 0
                    
                    # Direction'a göre sonuç döndür
                    if direction == 'NS':
                        if score_ns:
                            return {
                                'pair_names': pair_names,
                                'direction': 'NS',
                                'contract': contract,
                                'declarer': declarer,
                                'result': result_text,
                                'lead': lead,
                                'score': score_ns,
                                'percent': pct_ns
                            }
                        elif score_ew:
                            # NS skorlu ama EW kolonunda (negatif skor NS için)
                            return {
                                'pair_names': pair_names,
                                'direction': 'NS',
                                'contract': contract,
                                'declarer': declarer,
                                'result': result_text,
                                'lead': lead,
                                'score': f"-{score_ew}",
                                'percent': pct_ns
                            }
                    elif direction == 'EW':
                        # EW yüzdesi = 100 - NS yüzdesi
                        pct_ew = round(100 - pct_ns, 2)
                        if score_ew:
                            return {
                                'pair_names': pair_names,
                                'direction': 'EW',
                                'contract': contract,
                                'declarer': declarer,
                                'result': result_text,
                                'lead': lead,
                                'score': score_ew,
                                'percent': pct_ew
                            }
                        elif score_ns:
                            # EW skorlu ama NS kolonunda (negatif skor EW için)
                            return {
                                'pair_names': pair_names,
                                'direction': 'EW',
                                'contract': contract,
                                'declarer': declarer,
                                'result': result_text,
                                'lead': lead,
                                'score': f"-{score_ns}",
                                'percent': pct_ew
                            }
        return None
    except Exception as e:
        return None

def get_event_info(event_id):
    """Turnuva bilgilerini, çift sayısını ve pair isimlerini al"""
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
        
        # NS ve EW çiftlerini ve isimlerini bul
        ns_pairs = {}  # {pair_num: "Player1 - Player2"}
        ew_pairs = {}
        
        # colored tablosunu bul
        table = soup.find('table', class_='colored')
        if table:
            rows = table.find_all('tr')
            
            # İlk satırdan format belirle
            header_row = rows[0] if rows else None
            header_text = header_row.get_text(strip=True) if header_row else ""
            
            # Format 1: "Masa | Kuzey - Güney | IMP | Doğu - Batı" (IMP turnuvaları)
            if 'Masa' in header_text and 'Kuzey' in header_text and 'Doğu' in header_text:
                for row in rows[1:]:  # Header'ı atla
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 4:
                        masa_num = cells[0].get_text(strip=True)
                        if masa_num.isdigit():
                            pair_num = int(masa_num)
                            ns_name = cells[1].get_text(strip=True)
                            ew_name = cells[3].get_text(strip=True)
                            if ns_name:
                                ns_pairs[pair_num] = ns_name
                            if ew_name:
                                ew_pairs[pair_num] = ew_name
            
            # Format 2: "Sıra/Rank" ile ayrı NS ve EW bölümleri (MP turnuvaları)
            else:
                in_ns = False
                in_ew = False
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if not cells:
                        continue
                    
                    first_text = cells[0].get_text(strip=True)
                    
                    # Bölüm başlığı mı?
                    if 'Kuzey' in first_text or 'North' in first_text:
                        in_ns = True
                        in_ew = False
                        continue
                    elif 'Doğu' in first_text or 'East' in first_text:
                        in_ew = True
                        in_ns = False
                        continue
                    elif first_text in ['Sıra', 'Rank']:
                        continue
                    
                    # Veri satırı mı?
                    if len(cells) >= 3 and first_text.isdigit():
                        pair_num = int(first_text)
                        # 2. hücre: "Player1 - Player2" formatında
                        pair_name = cells[1].get_text(strip=True)
                        
                        if in_ns:
                            ns_pairs[pair_num] = pair_name
                        elif in_ew:
                            ew_pairs[pair_num] = pair_name
        
        return {
            'name': tournament_name,
            'date': tournament_date,
            'ns_pairs': len(ns_pairs) if ns_pairs else 13,
            'ew_pairs': len(ew_pairs) if ew_pairs else 13,
            'ns_pair_names': ns_pairs,
            'ew_pair_names': ew_pairs
        }
    except Exception as e:
        return {'name': '', 'date': '', 'ns_pairs': 13, 'ew_pairs': 13, 'ns_pair_names': {}, 'ew_pair_names': {}}

def fetch_board_results(event_id, board_num, ns_count, ew_count, ns_pair_names=None, ew_pair_names=None):
    """Bir board için tüm sonuçları çeker (paralel)"""
    all_results = []
    tasks = []
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # NS çiftleri
        for pair_num in range(1, ns_count + 1):
            tasks.append(executor.submit(fetch_pair_result, event_id, board_num, pair_num, 'NS', 'A', ns_pair_names))
        # EW çiftleri
        for pair_num in range(1, ew_count + 1):
            tasks.append(executor.submit(fetch_pair_result, event_id, board_num, pair_num, 'EW', 'A', ew_pair_names))
        
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
        # IMP event'leri atla
        if event_id in IMP_EVENTS:
            print(f"\n[SKIP] Event {event_id} - IMP turnuvası, atlanıyor")
            processed += len(event_info['boards'])
            skipped += len(event_info['boards'])
            continue
            
        print(f"\n{'='*60}")
        print(f"Event {event_id} - {event_info['date']}")
        
        # Event bilgilerini çek
        if event_id not in result_data['events'] or 'ns_pair_names' not in result_data['events'].get(event_id, {}):
            info = get_event_info(event_id)
            result_data['events'][event_id] = {
                'name': info['name'],
                'date': info['date'],
                'ns_pairs': info['ns_pairs'],
                'ew_pairs': info['ew_pairs'],
                'ns_pair_names': info.get('ns_pair_names', {}),
                'ew_pair_names': info.get('ew_pair_names', {})
            }
            ns_pair_names = info.get('ns_pair_names', {})
            ew_pair_names = info.get('ew_pair_names', {})
            print(f"  {info['name']} - NS:{info['ns_pairs']} EW:{info['ew_pairs']}")
        else:
            info = result_data['events'][event_id]
            ns_pair_names = info.get('ns_pair_names', {})
            ew_pair_names = info.get('ew_pair_names', {})
        
        # Her board için
        for board_num in sorted(event_info['boards']):
            board_key = f"{event_id}_{board_num}"
            
            # Zaten varsa atla
            if board_key in result_data['boards'] and len(result_data['boards'][board_key].get('results', [])) > 0:
                skipped += 1
                processed += 1
                continue
            
            print(f"  Board {board_num}...", end=' ', flush=True)
            start = time.time()
            
            results = fetch_board_results(event_id, board_num, info['ns_pairs'], info['ew_pairs'], ns_pair_names, ew_pair_names)
            
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
