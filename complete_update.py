#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BRIC Complete Data Update Pipeline
===================================
Tüm veri güncelleme işlemlerini sırasıyla çalıştırır:

1. Turnuva sonuçlarını güncelle (database.json, legacy_records)
2. El dağılımlarını güncelle (hands_database.json)
3. Board sonuçlarını güncelle (board_results.json) - YENİ!
4. Oyuncu sıralamalarını hesapla (player_rankings.json) - YENİ!

Windows Task Scheduler ile günde 1-2 kez çalıştırılabilir.
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import sys
import os
import time
import io
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://clubs.vugraph.com/hosgoru"
SCRIPT_DIR = Path(__file__).parent
DB_FILE = SCRIPT_DIR / 'database.json'
HANDS_DB_FILE = SCRIPT_DIR / 'hands_database.json'
BOARD_RESULTS_FILE = SCRIPT_DIR / 'board_results.json'
PLAYER_RANKINGS_FILE = SCRIPT_DIR / 'player_rankings.json'
LOG_FILE = SCRIPT_DIR / 'complete_update_log.txt'

BOARDS_PER_EVENT = 30
MAX_WORKERS = 10
REQUEST_TIMEOUT = 15

# ============================================================
# LOGGING
# ============================================================

def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] [{level}] {message}"
    print(log_msg)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_msg + '\n')

def log_section(title):
    log("=" * 60)
    log(title)
    log("=" * 60)

# ============================================================
# STEP 1: CALENDAR & EVENT DETECTION
# ============================================================

def get_calendar_events(month=None, year=None):
    """Takvimden tüm turnuvaları çek"""
    if month is None:
        month = datetime.now().month
    if year is None:
        year = datetime.now().year
    
    try:
        url = f"{BASE_URL}/calendar.php?month={month}&year={year}"
        response = requests.get(url, timeout=30)
        response.encoding = 'utf-8'
    except Exception as e:
        log(f"Takvim çekme hatası: {e}", "ERROR")
        return {}
    
    soup = BeautifulSoup(response.text, 'html.parser')
    events = {}
    
    # Tüm event linklerini bul
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        if 'eventresults.php?event=' in href:
            event_id = href.split('event=')[1].split('&')[0]
            event_name = link.get_text(strip=True)
            
            # Tarih bulmaya çalış - parent cell'den
            parent = link.find_parent('td', class_='days')
            date_str = ""
            if parent:
                day_cell = parent.find('td', class_='days2')
                if day_cell:
                    try:
                        day = int(day_cell.get_text(strip=True))
                        date_str = f"{day:02d}.{month:02d}.{year}"
                    except:
                        pass
            
            if event_id not in events:
                events[event_id] = {
                    'id': event_id,
                    'name': event_name,
                    'date': date_str
                }
    
    return events

# ============================================================
# STEP 2: TOURNAMENT SCORES UPDATE
# ============================================================

def fetch_event_results(event_id):
    """Bir turnuvanın sonuçlarını çek"""
    try:
        url = f"{BASE_URL}/eventresults.php?event={event_id}"
        response = requests.get(url, timeout=30)
        response.encoding = 'iso-8859-9'
    except Exception as e:
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    results = {'NS': [], 'EW': []}
    
    # Turnuva bilgileri
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
    
    # NS ve EW tablolarını bul
    tables = soup.find_all('table')
    current_direction = None
    
    for table in tables:
        prev = table.find_previous(['h4', 'h3', 'h2'])
        if prev:
            text = prev.get_text(strip=True)
            if 'Kuzey' in text or 'North' in text:
                current_direction = 'NS'
            elif 'Doğu' in text or 'East' in text:
                current_direction = 'EW'
        
        if current_direction:
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 3:
                    try:
                        rank = int(cells[0].get_text(strip=True))
                        names = cells[1].get_text(strip=True)
                        score = float(cells[2].get_text(strip=True).replace(',', '.'))
                        
                        results[current_direction].append({
                            'Sıra': rank,
                            'Tarih': tournament_date,
                            'Çift': names,
                            'Skor': score,
                            'Direction': current_direction,
                            'Turnuva': f"{tournament_name} ({tournament_date})"
                        })
                    except:
                        continue
    
    return {
        'name': tournament_name,
        'date': tournament_date,
        'results': results
    }

# ============================================================
# STEP 3: HANDS UPDATE
# ============================================================

def fetch_board_hands(event_id, board_num):
    """Bir board'un el dağılımını çek"""
    try:
        url = f"{BASE_URL}/boarddetails.php?event={event_id}&section=A&pair=1&direction=NS&board={board_num}"
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.encoding = 'iso-8859-9'
    except Exception as e:
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Tarih al
    date_str = ""
    h3 = soup.find('h3')
    if h3:
        h3_text = h3.get_text(strip=True)
        date_match = re.search(r'(\d{2})-(\d{2})-(\d{4})', h3_text)
        if date_match:
            day, month, year = date_match.groups()
            date_str = f"{day}.{month}.{year}"
    
    # El dağılımını bul - tablo içinde
    hands = {'N': '', 'S': '', 'E': '', 'W': ''}
    
    for table in soup.find_all('table'):
        text = table.get_text()
        if 'spades' in text and 'hearts' in text:
            cells = table.find_all('td')
            for cell in cells:
                cell_text = cell.get_text(strip=True)
                # Pattern: İSİM spades XX hearts XX diamonds XX clubs XX
                if 'spades' in cell_text.lower():
                    match = re.search(r'spades\s*([^\s]+)\s*hearts\s*([^\s]+)\s*diamonds\s*([^\s]+)\s*clubs\s*([^\s]+)', cell_text, re.IGNORECASE)
                    if match:
                        s, h, d, c = match.groups()
                        hand_str = f"{s}.{h}.{d}.{c}"
                        
                        # Pozisyonu belirle
                        parent_row = cell.find_parent('tr')
                        if parent_row:
                            row_cells = parent_row.find_all('td')
                            cell_index = row_cells.index(cell) if cell in row_cells else -1
                            
                            # Basit pozisyon tahmini
                            all_rows = table.find_all('tr')
                            row_index = all_rows.index(parent_row) if parent_row in all_rows else -1
                            
                            if row_index == 0:
                                hands['N'] = hand_str
                            elif row_index == 2:
                                hands['S'] = hand_str
                            elif cell_index == 0:
                                hands['W'] = hand_str
                            elif cell_index == 2:
                                hands['E'] = hand_str
    
    if any(hands.values()):
        return {
            'event_id': event_id,
            'Tarih': date_str,
            'Board': board_num,
            'N': hands['N'],
            'S': hands['S'],
            'E': hands['E'],
            'W': hands['W'],
            'Dealer': '',
            'Vuln': ''
        }
    return None

# ============================================================
# STEP 4: BOARD RESULTS UPDATE
# ============================================================

def parse_contract_cell(cell):
    """Kontrat hücresini parse et"""
    text = cell.get_text(strip=True)
    suit_map = {'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣'}
    for img in cell.find_all('img'):
        alt = img.get('alt', '')
        if alt in suit_map:
            text = text.replace('', suit_map[alt])
    for code, symbol in suit_map.items():
        if code in text:
            text = text.replace(code, symbol)
    return text

def parse_lead_cell(cell):
    """Atak hücresini parse et"""
    text = cell.get_text(strip=True)
    suit_map = {'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣'}
    for img in cell.find_all('img'):
        alt = img.get('alt', '')
        if alt in suit_map:
            text = text.replace(alt, suit_map[alt])
    for code, symbol in suit_map.items():
        if code in text:
            text = text.replace(code, symbol)
    return text

def fetch_pair_board_result(event_id, board_num, pair_num, direction, section='A'):
    """Bir çiftin bir board sonucunu çek"""
    try:
        url = f"{BASE_URL}/boarddetails.php?event={event_id}&section={section}&pair={pair_num}&direction={direction}&board={board_num}"
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
            if len(cells) >= 7:
                cell_class = cells[0].get('class', [''])[0] if cells[0].get('class') else ''
                if cell_class in ['fantastic', 'resultspecial', 'resultsimportant']:
                    contract = parse_contract_cell(cells[0])
                    declarer = cells[1].get_text(strip=True)
                    result_text = cells[2].get_text(strip=True)
                    
                    # 8 hücre veya 7 hücre format
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
    except:
        return None

def get_event_pair_counts(event_id):
    """Turnuvadaki NS ve EW çift sayılarını al"""
    try:
        url = f"{BASE_URL}/eventresults.php?event={event_id}"
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.encoding = 'iso-8859-9'
        soup = BeautifulSoup(resp.content, 'html.parser')
        
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
        
        return ns_count or 13, ew_count or 13
    except:
        return 13, 13

def fetch_board_all_results(event_id, board_num, ns_count, ew_count):
    """Bir board için tüm sonuçları paralel çek"""
    all_results = []
    tasks = []
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for pair_num in range(1, ns_count + 1):
            tasks.append(executor.submit(fetch_pair_board_result, event_id, board_num, pair_num, 'NS'))
        for pair_num in range(1, ew_count + 1):
            tasks.append(executor.submit(fetch_pair_board_result, event_id, board_num, pair_num, 'EW'))
        
        for future in as_completed(tasks):
            result = future.result()
            if result:
                all_results.append(result)
    
    # Sırala
    all_results.sort(key=lambda x: x['percent'], reverse=True)
    for i, r in enumerate(all_results):
        r['rank'] = i + 1
    
    return all_results

# ============================================================
# STEP 5: PLAYER RANKINGS
# ============================================================

def calculate_player_rankings(board_results, min_boards=10):
    """Oyuncu sıralaması hesapla"""
    from collections import defaultdict
    
    player_stats = defaultdict(lambda: {'total_percent': 0, 'board_count': 0, 'events': set()})
    
    for board_key, board_data in board_results.get('boards', {}).items():
        event_id = board_data.get('event_id', '')
        
        for result in board_data.get('results', []):
            pair_names = result.get('pair_names', '')
            percent = result.get('percent', 0)
            
            if not pair_names or ' - ' not in pair_names:
                continue
            
            players = pair_names.split(' - ')
            if len(players) != 2:
                continue
            
            for player in players:
                player = player.strip()
                player_stats[player]['total_percent'] += percent
                player_stats[player]['board_count'] += 1
                player_stats[player]['events'].add(event_id)
    
    rankings = []
    for player, stats in player_stats.items():
        if stats['board_count'] >= min_boards:
            avg = stats['total_percent'] / stats['board_count']
            rankings.append({
                'player': player,
                'average': round(avg, 2),
                'board_count': stats['board_count'],
                'event_count': len(stats['events'])
            })
    
    rankings.sort(key=lambda x: x['average'], reverse=True)
    for i, r in enumerate(rankings):
        r['rank'] = i + 1
    
    return rankings

# ============================================================
# MAIN UPDATE PIPELINE
# ============================================================

def run_complete_update():
    """Tam güncelleme pipeline'ı çalıştır"""
    start_time = time.time()
    log_section("BRIC COMPLETE DATA UPDATE")
    log(f"Başlangıç: {datetime.now()}")
    
    # Mevcut verileri yükle
    log("Mevcut veriler yükleniyor...")
    
    # Database
    if DB_FILE.exists():
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            database = json.load(f)
    else:
        database = {'version': '2.0', 'events': {}, 'legacy_records': []}
    
    # Hands
    if HANDS_DB_FILE.exists():
        with open(HANDS_DB_FILE, 'r', encoding='utf-8') as f:
            hands_db = json.load(f)
    else:
        hands_db = []
    
    # Board Results
    if BOARD_RESULTS_FILE.exists():
        with open(BOARD_RESULTS_FILE, 'r', encoding='utf-8') as f:
            board_results = json.load(f)
    else:
        board_results = {'version': '1.0', 'events': {}, 'boards': {}}
    
    existing_event_ids = set(board_results.get('events', {}).keys())
    existing_hands = {(h['event_id'], h['Board']) for h in hands_db}
    existing_boards = set(board_results.get('boards', {}).keys())
    
    log(f"  Database: {len(database.get('legacy_records', []))} kayıt")
    log(f"  Hands: {len(hands_db)} el")
    log(f"  Board Results: {len(existing_boards)} board")
    
    # Takvimden turnuvaları çek
    log_section("STEP 1: TURNUVA TESPİTİ")
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    all_events = {}
    for month in range(1, current_month + 1):
        events = get_calendar_events(month, current_year)
        all_events.update(events)
        log(f"  {month}/{current_year}: {len(events)} turnuva")
    
    log(f"Toplam {len(all_events)} turnuva tespit edildi")
    
    # Yeni turnuvaları bul
    new_event_ids = set(all_events.keys()) - existing_event_ids
    log(f"Yeni turnuva: {len(new_event_ids)}")
    
    if not new_event_ids:
        log("Yeni turnuva yok, mevcut veriler güncel.")
    else:
        # Her yeni turnuva için
        for event_id in sorted(new_event_ids):
            event_info = all_events[event_id]
            log(f"\nTurnuva: {event_id} - {event_info.get('name', '?')}")
            
            # Çift sayılarını al
            ns_count, ew_count = get_event_pair_counts(event_id)
            log(f"  NS: {ns_count}, EW: {ew_count}")
            
            board_results['events'][event_id] = {
                'name': event_info.get('name', ''),
                'date': event_info.get('date', ''),
                'ns_pairs': ns_count,
                'ew_pairs': ew_count
            }
            
            # Her board için
            for board_num in range(1, BOARDS_PER_EVENT + 1):
                board_key = f"{event_id}_{board_num}"
                
                if board_key in existing_boards:
                    continue
                
                # El dağılımı
                hand_key = (event_id, board_num)
                if hand_key not in existing_hands:
                    hand_data = fetch_board_hands(event_id, board_num)
                    if hand_data and any([hand_data.get('N'), hand_data.get('S'), hand_data.get('E'), hand_data.get('W')]):
                        hands_db.append(hand_data)
                        existing_hands.add(hand_key)
                
                # Board sonuçları
                results = fetch_board_all_results(event_id, board_num, ns_count, ew_count)
                board_results['boards'][board_key] = {
                    'event_id': event_id,
                    'board': board_num,
                    'date': event_info.get('date', ''),
                    'results': results
                }
                existing_boards.add(board_key)
                
                log(f"  Board {board_num}: {len(results)} sonuç")
                
                # Her 10 board'da kaydet
                if len(existing_boards) % 10 == 0:
                    board_results['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    with open(BOARD_RESULTS_FILE, 'w', encoding='utf-8') as f:
                        json.dump(board_results, f, ensure_ascii=False, indent=2)
    
    # Final kayıt
    log_section("STEP 2: VERİLERİ KAYDET")
    
    board_results['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(BOARD_RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(board_results, f, ensure_ascii=False, indent=2)
    log(f"Board Results: {len(board_results['boards'])} board kaydedildi")
    
    with open(HANDS_DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(hands_db, f, ensure_ascii=False, indent=2)
    log(f"Hands: {len(hands_db)} el kaydedildi")
    
    # Oyuncu sıralaması
    log_section("STEP 3: OYUNCU SIRALAMASI")
    rankings = calculate_player_rankings(board_results, min_boards=10)
    
    rankings_data = {
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_players': len(rankings),
        'min_boards': 10,
        'rankings': rankings
    }
    
    with open(PLAYER_RANKINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(rankings_data, f, ensure_ascii=False, indent=2)
    log(f"Oyuncu sıralaması: {len(rankings)} oyuncu")
    
    # Özet
    elapsed = time.time() - start_time
    log_section("GÜNCELLEME TAMAMLANDI")
    log(f"Süre: {elapsed:.1f} saniye")
    log(f"Board Results: {len(board_results['boards'])} board")
    log(f"Hands: {len(hands_db)} el")
    log(f"Rankings: {len(rankings)} oyuncu")

if __name__ == '__main__':
    run_complete_update()
