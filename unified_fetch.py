#!/usr/bin/env python3
"""
Unified Data Fetcher - Tüm veri çekme işlemlerini tek noktadan yönetir.

Bu script:
1. Yeni turnuvaları otomatik tespit eder
2. El verilerini (hands) çeker
3. Board sıralaması verilerini (rankings) çeker
4. Tüm event ID'lerin tutarlılığını sağlar

Kullanım:
    python unified_fetch.py                    # Eksik tüm verileri çek
    python unified_fetch.py --hands-only       # Sadece el verilerini çek
    python unified_fetch.py --rankings-only    # Sadece sıralama verilerini çek
    python unified_fetch.py --date 21.01.2026  # Belirli tarih için çek
    python unified_fetch.py --daemon           # 30 dakikada bir çalış
    python unified_fetch.py --validate         # Veri tutarlılığını kontrol et
"""

import json
import time
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from pathlib import Path
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Set, Optional, Tuple

# Try to import Selenium for JavaScript-rendered pages
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# Local imports
try:
    from event_registry import EventRegistry, get_event_id
except ImportError:
    # Fallback if event_registry not available
    EventRegistry = None
    get_event_id = None

# === Configuration ===
BASE_PATH = Path(__file__).parent
DATABASE_FILE = BASE_PATH / "database.json"
HANDS_FILE = BASE_PATH / "hands_database.json"
BOARD_RESULTS_FILE = BASE_PATH / "board_results.json"

BASE_URL = "https://clubs.vugraph.com/hosgoru"
REQUEST_TIMEOUT = 15
MAX_WORKERS = 5

# IMP turnuvaları - yüzde yerine IMP kullanır
IMP_EVENTS = {'405080', '405171', '405248', '405321'}


class DataFetcher:
    """Unified data fetching class"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.registry = EventRegistry() if EventRegistry else None
        
        # Load existing data
        self.database = self._load_json(DATABASE_FILE, {"version": "2.0", "events": {}, "legacy_records": []})
        self.hands = self._load_json(HANDS_FILE, [])
        self.board_results = self._load_json(BOARD_RESULTS_FILE, {"version": "1.0", "boards": {}})
        
        # Caches
        self._hands_events: Set[str] = set()
        self._hands_boards: Dict[str, Set[int]] = {}
        self._results_boards: Dict[str, Set[int]] = {}
        
        self._build_caches()
    
    def _load_json(self, path: Path, default):
        """JSON dosyasını yükle"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default
    
    def _save_json(self, path: Path, data):
        """JSON dosyasını kaydet"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _build_caches(self):
        """Hızlı erişim için cache'leri oluştur"""
        # hands_database cache
        for h in self.hands:
            event_id = str(h.get('event_id', ''))
            board = h.get('Board')
            if event_id:
                self._hands_events.add(event_id)
                if event_id not in self._hands_boards:
                    self._hands_boards[event_id] = set()
                if board:
                    self._hands_boards[event_id].add(board)
        
        # board_results cache
        for key in self.board_results.get('boards', {}).keys():
            parts = key.split('_')
            if len(parts) == 2:
                event_id, board = parts[0], int(parts[1])
                if event_id not in self._results_boards:
                    self._results_boards[event_id] = set()
                self._results_boards[event_id].add(board)
    
    def log(self, msg: str):
        """Log mesajı yazdır"""
        if self.verbose:
            print(msg)
    
    # === Event ID Resolution ===
    
    def get_event_id_for_date(self, date: str) -> Optional[str]:
        """Tarih için event ID al - registry veya database'den"""
        if self.registry:
            event_id = self.registry.get_event_id(date)
            if event_id:
                return event_id
        
        # Fallback: database.json'dan ara
        for record in self.database.get('legacy_records', []):
            if record.get('Tarih') == date:
                link = record.get('Link', '')
                match = re.search(r'event=(\d+)', link)
                if match:
                    return match.group(1)
        
        return None
    
    def get_date_for_event(self, event_id: str) -> Optional[str]:
        """Event ID için tarih al"""
        if self.registry:
            return self.registry.get_date(event_id)
        
        for record in self.database.get('legacy_records', []):
            link = record.get('Link', '')
            if f'event={event_id}' in link:
                return record.get('Tarih')
        return None
    
    # === Vugraph Data Fetching ===
    
    def fetch_event_info(self, event_id: str) -> dict:
        """Turnuva bilgilerini ve pair sayılarını al"""
        try:
            url = f'{BASE_URL}/eventresults.php?event={event_id}'
            resp = requests.get(url, timeout=REQUEST_TIMEOUT)
            resp.encoding = 'iso-8859-9'
            soup = BeautifulSoup(resp.content, 'html.parser')
            
            # Pair isimlerini ve sayılarını çıkar
            ns_pairs = {}
            ew_pairs = {}
            
            table = soup.find('table', class_='colored')
            if table:
                rows = table.find_all('tr')
                in_ns, in_ew = False, False
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if not cells:
                        continue
                    
                    first_text = cells[0].get_text(strip=True)
                    
                    if 'Kuzey' in first_text or 'North' in first_text:
                        in_ns, in_ew = True, False
                        continue
                    elif 'Doğu' in first_text or 'East' in first_text:
                        in_ns, in_ew = False, True
                        continue
                    elif first_text in ['Sıra', 'Rank']:
                        continue
                    
                    if len(cells) >= 3 and first_text.isdigit():
                        pair_num = int(first_text)
                        pair_name = cells[1].get_text(strip=True)
                        
                        if in_ns:
                            ns_pairs[pair_num] = pair_name
                        elif in_ew:
                            ew_pairs[pair_num] = pair_name
            
            return {
                'ns_count': len(ns_pairs) or 13,
                'ew_count': len(ew_pairs) or 13,
                'ns_names': ns_pairs,
                'ew_names': ew_pairs
            }
        except Exception as e:
            return {'ns_count': 13, 'ew_count': 13, 'ns_names': {}, 'ew_names': {}}
    
    def fetch_hands_for_event(self, event_id: str) -> List[dict]:
        """Bir event için el verilerini çek (Selenium fallback ile)"""
        hands = []
        date = self.get_date_for_event(event_id)
        
        # Önce normal yöntemle çek
        hands = self._fetch_hands_regular(event_id, date)
        
        # Eğer hiç el çekilemediyse ve Selenium kullanılabilirse, Selenium'u kullan
        if not hands and SELENIUM_AVAILABLE:
            hands = self._fetch_hands_selenium(event_id, date)
        
        return hands
    
    def _fetch_hands_regular(self, event_id: str, date: str) -> List[dict]:
        """Normal method ile hands çek"""
        hands = []
        
        for board_num in range(1, 31):
            url = f'{BASE_URL}/boarddetails.php?event={event_id}&section=A&pair=1&direction=NS&board={board_num}'
            
            try:
                resp = requests.get(url, timeout=REQUEST_TIMEOUT)
                resp.encoding = 'iso-8859-9'
                
                if 'Page not Found' in resp.text:
                    continue
                
                soup = BeautifulSoup(resp.content, 'html.parser')
                
                # Hand diagram parsing
                hand_data = self._parse_hand_diagram(soup)
                if hand_data:
                    hand_data['event_id'] = event_id
                    hand_data['date'] = date
                    hand_data['board'] = board_num
                    # Calculate dealer based on board number (standard bridge convention)
                    dealers = ['N', 'E', 'S', 'W']
                    hand_data['dealer'] = dealers[(board_num - 1) % 4]
                    hands.append(hand_data)
                    
            except Exception as e:
                continue
        
        return hands
    
    def _fetch_hands_selenium(self, event_id: str, date: str) -> List[dict]:
        """Selenium ile JavaScript-rendered hands çek"""
        hands = []
        
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            
            driver = webdriver.Chrome(options=options)
            
            for board_num in range(1, 31):
                url = f'{BASE_URL}/boarddetails.php?event={event_id}&section=A&pair=1&direction=NS&board={board_num}'
                
                try:
                    driver.get(url)
                    time.sleep(1)  # Wait for page load
                    
                    page_html = driver.page_source
                    
                    if 'Page not Found' in page_html:
                        continue
                    
                    soup = BeautifulSoup(page_html, 'html.parser')
                    hand_data = self._parse_hand_diagram(soup)
                    
                    if hand_data:
                        hand_data['event_id'] = event_id
                        hand_data['date'] = date
                        hand_data['board'] = board_num
                        # Calculate dealer based on board number (standard bridge convention)
                        dealers = ['N', 'E', 'S', 'W']
                        hand_data['dealer'] = dealers[(board_num - 1) % 4]
                        hands.append(hand_data)
                        
                except Exception as e:
                    continue
            
            driver.quit()
            
        except Exception as e:
            pass  # Selenium failed, return empty
        
        return hands
    
    def _parse_hand_diagram(self, soup) -> Optional[dict]:
        """HTML'den el dağılımını parse et - RAW COMPASS POSITIONS ONLY (NO ROTATION)"""
        try:
            # PROVEN METHOD: Look for bridgetable with oyuncu class cells
            bridge_table = soup.find('table', class_='bridgetable')
            if not bridge_table:
                return None
            
            hands = {
                'N': {'S': '', 'H': '', 'D': '', 'C': ''},
                'S': {'S': '', 'H': '', 'D': '', 'C': ''},
                'E': {'S': '', 'H': '', 'D': '', 'C': ''},
                'W': {'S': '', 'H': '', 'D': '', 'C': ''}
            }
            
            # Get player cells (oyuncu class)
            player_cells = bridge_table.find_all('td', class_='oyuncu')
            
            if len(player_cells) < 4:
                return None
            
            # HTML table lists player cells in vugraph order: N (top), W (left), E (right), S (bottom)
            # Map vugraph HTML positions DIRECTLY to compass positions (no rotation)
            visual_to_compass = {
                0: 'N',  # Position 0: North (top player)
                1: 'W',  # Position 1: West (left side player)
                2: 'E',  # Position 2: East (right side player)
                3: 'S'   # Position 3: South (bottom player)
            }
            
            for idx, cell in enumerate(player_cells):
                if idx >= 4:
                    break
                
                compass_pos = visual_to_compass[idx]
                
                # Find all img tags with suit images
                suit_imgs = cell.find_all('img')
                
                # Extract suits and cards
                for img in suit_imgs:
                    # Get the alt attribute to determine suit
                    alt_text = img.get('alt', '').lower()
                    
                    suit = None
                    if 'spade' in alt_text:
                        suit = 'S'
                    elif 'heart' in alt_text:
                        suit = 'H'
                    elif 'diamond' in alt_text:
                        suit = 'D'
                    elif 'club' in alt_text:
                        suit = 'C'
                    
                    if not suit:
                        continue
                    
                    # Get text immediately after the img tag
                    next_elem = img.next_sibling
                    cards = ''
                    
                    while next_elem:
                        if isinstance(next_elem, str):
                            text = str(next_elem).strip()
                            if text and text != '<br />' and text != '-':
                                cards = text.replace('<br />', '').replace('\n', '').strip()
                                break
                            if text == '-':
                                cards = ''
                                break
                        next_elem = next_elem.next_sibling
                    
                    if cards:
                        hands[compass_pos][suit] = cards
            
            # Convert extracted compass positions to PBN format (NO rotation applied)
            for direction in ['N', 'S', 'E', 'W']:
                spades = hands[direction].get('S', '')
                hearts = hands[direction].get('H', '')
                diamonds = hands[direction].get('D', '')
                clubs = hands[direction].get('C', '')
                pbn_hand = f"{spades}.{hearts}.{diamonds}.{clubs}"
                if any([spades, hearts, diamonds, clubs]):
                    hands[direction] = pbn_hand
                else:
                    hands[direction] = None
            
            # Return hands in RAW compass positions (N=North, E=East, S=South, W=West)
            result = {}
            for direction in ['N', 'S', 'E', 'W']:
                if hands[direction]:
                    result[direction] = hands[direction]
            
            if result and len(result) >= 3:
                return result
            
            return None
            
        except:
            return None
    
    def _parse_contract_cell(self, cell) -> str:
        """Kontrat hücresini parse et"""
        text = cell.get_text(strip=True)
        suit_map = {'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣'}
        for code, symbol in suit_map.items():
            text = text.replace(code, symbol)
        return text
    
    def _parse_lead_cell(self, cell) -> str:
        """Atak hücresini parse et"""
        text = cell.get_text(strip=True)
        suit_map = {'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣'}
        for code, symbol in suit_map.items():
            text = text.replace(code, symbol)
        return text
    
    def fetch_pair_result(self, event_id: str, board_num: int, pair_num: int, 
                          direction: str, pair_names_dict: dict) -> Optional[dict]:
        """Bir çift için board sonucunu çek"""
        try:
            # Her zaman NS sayfasını kullan
            url = f'{BASE_URL}/boarddetails.php?event={event_id}&section=A&pair={pair_num}&direction=NS&board={board_num}'
            resp = requests.get(url, timeout=REQUEST_TIMEOUT)
            resp.encoding = 'iso-8859-9'
            
            if 'Page not Found' in resp.text:
                return None
            
            soup = BeautifulSoup(resp.content, 'html.parser')
            
            # Pair ismi
            pair_names = ""
            if direction == 'NS':
                h3 = soup.find('h3')
                if h3:
                    h3_text = h3.get_text(strip=True)
                    match = re.search(r'\d{2}:\d{2}\s*\.\.\.\s*(.+?)\s*\.\.\.\s*Bord', h3_text)
                    if match:
                        pair_names = match.group(1).strip()
            
            if not pair_names and pair_num in pair_names_dict:
                pair_names = pair_names_dict[pair_num]
            
            if not pair_names:
                return None
            
            # Sonuç tablosu
            results_table = soup.find('table', class_='results')
            if not results_table:
                return None
            
            rows = results_table.find_all('tr')
            if not rows:
                return None
            
            # Highlighted satırı bul
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 7:
                    cell_class = cells[0].get('class', [''])[0] if cells[0].get('class') else ''
                    if cell_class in ['fantastic', 'resultspecial', 'resultsimportant']:
                        contract = self._parse_contract_cell(cells[0])
                        if not contract or contract in ['-6', '-', '']:
                            return None
                        
                        declarer = cells[1].get_text(strip=True)
                        result_text = cells[2].get_text(strip=True)
                        
                        # 8 vs 7 cell format
                        if len(cells) >= 8:
                            lead = self._parse_lead_cell(cells[3])
                            score_ns = cells[4].get_text(strip=True) if not cells[4].find('img') else ''
                            score_ew = cells[5].get_text(strip=True) if not cells[5].find('img') else ''
                            pct_ns_str = cells[6].get_text(strip=True) if not cells[6].find('img') else ''
                        else:
                            lead = ''
                            score_ns = cells[3].get_text(strip=True) if not cells[3].find('img') else ''
                            score_ew = cells[4].get_text(strip=True) if not cells[4].find('img') else ''
                            pct_ns_str = cells[5].get_text(strip=True) if not cells[5].find('img') else ''
                        
                        pct_ns = float(pct_ns_str) if pct_ns_str else 0
                        
                        if direction == 'NS':
                            score = score_ns if score_ns else (f"-{score_ew}" if score_ew else '')
                            return {
                                'pair_names': pair_names,
                                'direction': 'NS',
                                'contract': contract,
                                'declarer': declarer,
                                'result': result_text,
                                'lead': lead,
                                'score': score,
                                'percent': pct_ns
                            }
                        else:  # EW
                            pct_ew = round(100 - pct_ns, 2)
                            score = score_ew if score_ew else (f"-{score_ns}" if score_ns else '')
                            return {
                                'pair_names': pair_names,
                                'direction': 'EW',
                                'contract': contract,
                                'declarer': declarer,
                                'result': result_text,
                                'lead': lead,
                                'score': score,
                                'percent': pct_ew
                            }
            
            return None
        except:
            return None
    
    def fetch_board_results(self, event_id: str, board_num: int, 
                           ns_count: int, ew_count: int,
                           ns_names: dict, ew_names: dict) -> List[dict]:
        """Bir board için tüm sonuçları paralel çek"""
        results = []
        tasks = []
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # NS pairs
            for pair_num in range(1, ns_count + 1):
                tasks.append(executor.submit(
                    self.fetch_pair_result, event_id, board_num, pair_num, 'NS', ns_names
                ))
            # EW pairs
            for pair_num in range(1, ew_count + 1):
                tasks.append(executor.submit(
                    self.fetch_pair_result, event_id, board_num, pair_num, 'EW', ew_names
                ))
            
            for future in as_completed(tasks):
                result = future.result()
                if result:
                    results.append(result)
        
        # Sort by percent and add rank
        results.sort(key=lambda x: x['percent'], reverse=True)
        for i, r in enumerate(results):
            r['rank'] = i + 1
        
        return results
    
    # === Main Operations ===
    
    def get_missing_rankings(self) -> Dict[str, List[int]]:
        """Eksik sıralama verilerini bul"""
        missing = {}
        
        for event_id, boards in self._hands_boards.items():
            existing = self._results_boards.get(event_id, set())
            missing_boards = boards - existing
            if missing_boards:
                missing[event_id] = sorted(missing_boards)
        
        return missing
    
    def fetch_missing_rankings(self, limit: int = None) -> int:
        """Eksik sıralama verilerini çek"""
        missing = self.get_missing_rankings()
        
        if not missing:
            self.log("Eksik sıralama verisi yok.")
            return 0
        
        total_missing = sum(len(boards) for boards in missing.values())
        self.log(f"Toplam {len(missing)} event, {total_missing} eksik board bulundu.")
        
        fetched = 0
        
        for event_id, boards in missing.items():
            if limit and fetched >= limit:
                break
            
            date = self.get_date_for_event(event_id)
            self.log(f"\n=== Event {event_id} ({date}) ===")
            
            # Event bilgilerini al
            info = self.fetch_event_info(event_id)
            self.log(f"  NS: {info['ns_count']}, EW: {info['ew_count']}")
            
            for board_num in boards:
                if limit and fetched >= limit:
                    break
                
                start_time = time.time()
                results = self.fetch_board_results(
                    event_id, board_num,
                    info['ns_count'], info['ew_count'],
                    info['ns_names'], info['ew_names']
                )
                
                if results:
                    key = f"{event_id}_{board_num}"
                    self.board_results['boards'][key] = {
                        'event_id': event_id,
                        'board': board_num,
                        'date': date,
                        'results': results
                    }
                    fetched += 1
                    
                    elapsed = time.time() - start_time
                    self.log(f"  Board {board_num}: {len(results)} sonuç ({elapsed:.1f}s)")
                    
                    # Her 10 board'da kaydet
                    if fetched % 10 == 0:
                        self._save_board_results()
        
        # Son kayıt
        self._save_board_results()
        self.log(f"\nToplam {fetched} board çekildi.")
        return fetched
    
    def _save_board_results(self):
        """Board results'ı kaydet"""
        self.board_results['last_updated'] = datetime.now().isoformat()
        self._save_json(BOARD_RESULTS_FILE, self.board_results)
    
    def validate_data(self) -> dict:
        """Tüm verilerin tutarlılığını kontrol et"""
        issues = {
            'hands_event_id_issues': [],
            'missing_board_results': [],
            'orphan_board_results': []
        }
        
        # hands_database event ID kontrolü
        if self.registry:
            for i, hand in enumerate(self.hands):
                date = hand.get('Tarih')
                event_id = str(hand.get('event_id'))
                expected = self.registry.get_event_id(date)
                
                if expected and expected != event_id:
                    issues['hands_event_id_issues'].append({
                        'index': i,
                        'date': date,
                        'current': event_id,
                        'expected': expected
                    })
        
        # Eksik board_results
        missing = self.get_missing_rankings()
        issues['missing_board_results'] = [
            {'event_id': eid, 'boards': boards}
            for eid, boards in missing.items()
        ]
        
        # Orphan board_results (hands'te olmayan)
        for key in self.board_results.get('boards', {}).keys():
            event_id = key.split('_')[0]
            if event_id not in self._hands_events:
                issues['orphan_board_results'].append(key)
        
        return issues
    
    def fix_event_ids(self, dry_run: bool = True) -> int:
        """hands_database'deki event ID'leri düzelt"""
        if not self.registry:
            self.log("Event Registry mevcut değil, düzeltme yapılamaz.")
            return 0
        
        fixed = 0
        for i, hand in enumerate(self.hands):
            date = hand.get('Tarih')
            current_id = str(hand.get('event_id'))
            expected_id = self.registry.get_event_id(date)
            
            if expected_id and expected_id != current_id:
                if not dry_run:
                    self.hands[i]['event_id'] = expected_id
                fixed += 1
        
        if fixed > 0 and not dry_run:
            self._save_json(HANDS_FILE, self.hands)
            self.log(f"{fixed} kayıt düzeltildi.")
        else:
            self.log(f"{fixed} kayıt düzeltilecek (dry_run={dry_run})")
        
        return fixed
    
    def run_daemon(self, interval_minutes: int = 30):
        """Daemon modunda çalış"""
        self.log(f"Daemon modu başlatıldı. Her {interval_minutes} dakikada bir çalışacak.")
        
        while True:
            try:
                self.log(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Kontrol başlıyor...")
                
                # Reload data
                self.board_results = self._load_json(BOARD_RESULTS_FILE, {"version": "1.0", "boards": {}})
                self._results_boards.clear()
                self._build_caches()
                
                # Fetch missing
                self.fetch_missing_rankings()
                
            except Exception as e:
                self.log(f"[HATA] {e}")
            
            self.log(f"Sonraki kontrol: {interval_minutes} dakika sonra")
            time.sleep(interval_minutes * 60)


def main():
    parser = argparse.ArgumentParser(description='Unified Data Fetcher')
    parser.add_argument('--hands-only', action='store_true', help='Sadece el verilerini çek')
    parser.add_argument('--rankings-only', action='store_true', help='Sadece sıralama verilerini çek')
    parser.add_argument('--date', type=str, help='Belirli tarih için çek (DD.MM.YYYY)')
    parser.add_argument('--event', type=str, help='Belirli event ID için çek')
    parser.add_argument('--daemon', action='store_true', help='Daemon modunda çalış')
    parser.add_argument('--interval', type=int, default=30, help='Daemon aralığı (dakika)')
    parser.add_argument('--validate', action='store_true', help='Veri tutarlılığını kontrol et')
    parser.add_argument('--fix', action='store_true', help='Event ID tutarsızlıklarını düzelt')
    parser.add_argument('--limit', type=int, help='Maksimum board sayısı')
    parser.add_argument('--quiet', '-q', action='store_true', help='Sessiz mod')
    
    args = parser.parse_args()
    
    fetcher = DataFetcher(verbose=not args.quiet)
    
    if args.validate:
        issues = fetcher.validate_data()
        print("\n=== Veri Doğrulama Raporu ===")
        print(f"Event ID tutarsızlıkları: {len(issues['hands_event_id_issues'])}")
        print(f"Eksik board results: {sum(len(x['boards']) for x in issues['missing_board_results'])}")
        print(f"Orphan board results: {len(issues['orphan_board_results'])}")
        
        if issues['hands_event_id_issues']:
            print("\nEvent ID tutarsızlıkları (ilk 5):")
            for issue in issues['hands_event_id_issues'][:5]:
                print(f"  {issue['date']}: {issue['current']} -> {issue['expected']}")
        
        return
    
    if args.fix:
        fetcher.fix_event_ids(dry_run=False)
        return
    
    if args.daemon:
        fetcher.run_daemon(args.interval)
        return
    
    # Normal fetch
    fetcher.fetch_missing_rankings(limit=args.limit)


if __name__ == "__main__":
    main()
