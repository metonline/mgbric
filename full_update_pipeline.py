#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BRIC Full Update Pipeline
=========================
Tüm veri güncelleme işlemlerini zincirleme olarak çalıştırır:

1. Scores Update   - Turnuva sonuçlarını güncelle (Vugraph calendar)
2. Hands Update    - Turnuva ellerini çek (Vugraph boarddetails)
3. DD Analysis     - Yeni eller için Double Dummy analizi yap (endplay)
4. Site Analysis   - İstatistik ve raporları güncelle

Kullanım:
    python full_update_pipeline.py                  # Tam pipeline
    python full_update_pipeline.py --step scores    # Sadece scores
    python full_update_pipeline.py --step hands     # Sadece hands
    python full_update_pipeline.py --step dd        # Sadece DD analizi
    python full_update_pipeline.py --step analysis  # Sadece analiz
    python full_update_pipeline.py --force          # Tüm elleri tekrar analiz et
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
LOG_FILE = SCRIPT_DIR / 'pipeline_log.txt'
DD_RESULTS_FILE = SCRIPT_DIR / 'double_dummy' / 'dd_results.json'

# Board sayısı (varsayılan 30)
BOARDS_PER_EVENT = 30

# ============================================================
# LOGGING
# ============================================================

def log(message, level="INFO"):
    """Log message to console and file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] [{level}] {message}"
    print(log_msg)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_msg + '\n')


def log_section(title):
    """Log section header"""
    log("=" * 60)
    log(title)
    log("=" * 60)


# ============================================================
# STEP 1: SCORES UPDATE
# ============================================================

def get_calendar_events():
    """Fetch calendar and extract all events with their dates and IDs"""
    try:
        response = requests.get(f"{BASE_URL}/calendar.php", timeout=30)
        response.encoding = 'utf-8'
        response.raise_for_status()
    except Exception as e:
        log(f"Error fetching calendar: {e}", "ERROR")
        return {}
    
    soup = BeautifulSoup(response.text, 'html.parser')
    events_by_date = {}
    
    # Detect current month/year from calendar header
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    header = soup.find('th', colspan=True) or soup.find('td', class_='banner')
    if header:
        header_text = header.get_text(strip=True).lower()
        months_tr = {'ocak': 1, 'şubat': 2, 'mart': 3, 'nisan': 4, 'mayıs': 5, 'haziran': 6,
                    'temmuz': 7, 'ağustos': 8, 'eylül': 9, 'ekim': 10, 'kasım': 11, 'aralık': 12}
        months_en = {'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
                    'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12}
        
        for month_name, month_num in {**months_tr, **months_en}.items():
            if month_name in header_text:
                current_month = month_num
                break
        
        year_match = re.search(r'20\d{2}', header_text)
        if year_match:
            current_year = int(year_match.group())
    
    # Find all day cells in calendar grid
    day_cells = soup.find_all('td', class_='days')
    
    for cell in day_cells:
        day_num_cell = cell.find('td', class_='days2')
        if not day_num_cell:
            continue
        
        try:
            day = int(day_num_cell.get_text(strip=True))
        except ValueError:
            continue
        
        date_str = f"{day:02d}.{current_month:02d}.{current_year}"
        
        # Find all event links in this cell
        event_links = cell.find_all('a', href=True)
        for link in event_links:
            href = link.get('href', '')
            if 'eventresults.php?event=' in href:
                event_id = href.split('event=')[1]
                event_name = link.get_text(strip=True)
                
                if date_str not in events_by_date:
                    events_by_date[date_str] = []
                
                events_by_date[date_str].append({
                    'id': event_id,
                    'name': event_name,
                    'date': date_str
                })
    
    return events_by_date


def fetch_event_results(event_id, turnuva_name, tarih):
    """Parse tournament results from Vugraph event page"""
    url = f"{BASE_URL}/eventresults.php?event={event_id}"
    
    try:
        response = requests.get(url, timeout=30)
        response.encoding = 'utf-8'
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        records = []
        current_direction = None
        
        tables = soup.find_all('table', class_='colored')
        if not tables:
            return []
        
        table = tables[0]
        rows = table.find_all('tr')
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if not cells:
                continue
            
            if len(cells) == 1:
                text = cells[0].get_text(strip=True)
                if 'Kuzey' in text or 'North' in text:
                    current_direction = 'NS'
                elif 'Doğu' in text or 'Bati' in text or 'East' in text:
                    current_direction = 'EW'
                continue
            
            if len(cells) >= 3:
                first_cell = cells[0].get_text(strip=True)
                if first_cell in ['Sıra', 'Sira', 'Rank']:
                    continue
            
            if len(cells) >= 3 and current_direction:
                try:
                    sira_text = cells[0].get_text(strip=True)
                    pair_text = cells[1].get_text(strip=True)
                    skor_text = cells[2].get_text(strip=True)
                    
                    try:
                        sira = int(sira_text)
                    except ValueError:
                        continue
                    
                    skor = float(skor_text.replace(',', '.'))
                    
                    pair_parts = pair_text.split(' - ')
                    if len(pair_parts) >= 2:
                        oyuncu1 = pair_parts[0].strip()
                        oyuncu2 = ' - '.join(pair_parts[1:]).strip()
                        
                        record = {
                            'Sıra': sira,
                            'Tarih': tarih,
                            'Oyuncu 1': oyuncu1,
                            'Oyuncu 2': oyuncu2,
                            'Skor': skor,
                            'Direction': current_direction,
                            'Turnuva': turnuva_name,
                            'Link': url
                        }
                        records.append(record)
                
                except (ValueError, IndexError):
                    continue
        
        return records
    
    except Exception as e:
        log(f"Error fetching event {event_id}: {e}", "ERROR")
        return []


def update_scores():
    """Step 1: Update tournament scores database"""
    log_section("STEP 1: UPDATING TOURNAMENT SCORES")
    
    # Get calendar events
    events_by_date = get_calendar_events()
    log(f"Found {len(events_by_date)} dates with events in calendar")
    
    # Load current database
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        data = []
    
    # Get existing dates from database
    db_dates = set()
    if isinstance(data, dict) and 'events' in data:
        for event_data in data.get('events', {}).values():
            tarih = event_data.get('date')
            if tarih:
                db_dates.add(tarih)
        for record in data.get('legacy_records', []):
            tarih = record.get('Tarih')
            if tarih:
                db_dates.add(tarih)
    elif isinstance(data, list):
        for record in data:
            tarih = record.get('Tarih')
            if tarih:
                db_dates.add(tarih)
    
    log(f"Database has {len(db_dates)} unique dates")
    
    # Find missing dates
    missing_dates = [d for d in events_by_date.keys() if d not in db_dates]
    missing_dates.sort(key=lambda x: datetime.strptime(x, "%d.%m.%Y"))
    
    if not missing_dates:
        log("✓ Score database is up to date!")
        return True, []
    
    log(f"Found {len(missing_dates)} new date(s) to fetch: {missing_dates}")
    
    # Initialize if new format
    if isinstance(data, list):
        old_records = data
        data = {
            "version": "2.0",
            "last_updated": datetime.now().isoformat(),
            "events": {},
            "metadata": {"total_tournaments": 0, "total_boards": 0},
            "legacy_records": old_records
        }
    
    new_events = []
    
    # Fetch each missing date
    for tarih in missing_dates:
        events = events_by_date.get(tarih, [])
        log(f"Fetching {tarih}: {len(events)} event(s)")
        
        for event in events:
            turnuva_name = f"{event['name']} Sonuçları ({tarih} 14:00)"
            records = fetch_event_results(event['id'], turnuva_name, tarih)
            
            if records:
                ns_count = len([r for r in records if r.get('Direction') == 'NS'])
                ew_count = len([r for r in records if r.get('Direction') == 'EW'])
                log(f"  Event {event['id']}: {len(records)} records (NS: {ns_count}, EW: {ew_count})")
                
                event_key = f"event_{event['id']}"
                data['events'][event_key] = {
                    'id': event['id'],
                    'name': turnuva_name,
                    'date': tarih,
                    'results': {
                        'NS': [r for r in records if r.get('Direction') == 'NS'],
                        'EW': [r for r in records if r.get('Direction') == 'EW']
                    }
                }
                
                new_events.append({
                    'id': event['id'],
                    'date': tarih,
                    'name': turnuva_name
                })
                
                # Add to legacy_records
                if 'legacy_records' not in data:
                    data['legacy_records'] = []
                
                existing_legacy = set()
                for r in data['legacy_records']:
                    key = (r.get('Tarih'), r.get('Oyuncu 1'), r.get('Oyuncu 2'), r.get('Direction'))
                    existing_legacy.add(key)
                
                for record in records:
                    key = (record.get('Tarih'), record.get('Oyuncu 1'), record.get('Oyuncu 2'), record.get('Direction'))
                    if key not in existing_legacy:
                        data['legacy_records'].append(record)
    
    # Save database
    data['last_updated'] = datetime.now().isoformat()
    data['metadata']['total_tournaments'] = len(data['events'])
    
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        log(f"✓ Score database saved ({len(new_events)} new events)")
        return True, new_events
    except Exception as e:
        log(f"✗ Failed to save database: {e}", "ERROR")
        return False, []


# ============================================================
# STEP 2: HANDS UPDATE
# ============================================================

def extract_hands_from_page(html_content):
    """Extract hand information from Vugraph board detail page"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    hands = {
        'N': {'S': '', 'H': '', 'D': '', 'C': ''},
        'S': {'S': '', 'H': '', 'D': '', 'C': ''},
        'E': {'S': '', 'H': '', 'D': '', 'C': ''},
        'W': {'S': '', 'H': '', 'D': '', 'C': ''}
    }
    
    bridge_table = soup.find('table', class_='bridgetable')
    if not bridge_table:
        return None
    
    player_cells = bridge_table.find_all('td', class_='oyuncu')
    if len(player_cells) < 4:
        return None
    
    directions = ['W', 'N', 'E', 'S']
    
    for idx, cell in enumerate(player_cells[:4]):
        direction = directions[idx]
        suit_imgs = cell.find_all('img')
        
        for img in suit_imgs:
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
                hands[direction][suit] = cards
    
    return hands


def fetch_board_hands(event_id, board_num):
    """Fetch hand data for a specific board"""
    for section in ['A', 'B']:
        for pair in range(1, 25):
            url = f"{BASE_URL}/boarddetails.php?event={event_id}&section={section}&pair={pair}&direction=NS&board={board_num}"
            
            try:
                response = requests.get(url, timeout=10)
                response.encoding = 'utf-8'
                
                if response.status_code == 200 and 'bridgetable' in response.text:
                    hands = extract_hands_from_page(response.text)
                    if hands and any(h.get('S') or h.get('H') or h.get('D') or h.get('C') for h in hands.values()):
                        return hands
                
                time.sleep(0.05)
            except:
                continue
    
    return None


def get_dealer_for_board(board_num):
    """Standard bridge dealer rotation"""
    dealers = ['N', 'E', 'S', 'W']
    return dealers[(board_num - 1) % 4]


def get_vulnerability_for_board(board_num):
    """Standard bridge vulnerability rotation"""
    vul_pattern = [
        'None', 'NS', 'EW', 'Both',     # 1-4
        'NS', 'EW', 'Both', 'None',     # 5-8
        'EW', 'Both', 'None', 'NS',     # 9-12
        'Both', 'None', 'NS', 'EW'      # 13-16
    ]
    return vul_pattern[(board_num - 1) % 16]


def format_hand_for_bbo(hands):
    """Convert extracted hands to BBO viewer format (S.H.D.C)"""
    result = {}
    for direction in ['N', 'S', 'E', 'W']:
        s = hands[direction].get('S', '') or '-'
        h = hands[direction].get('H', '') or '-'
        d = hands[direction].get('D', '') or '-'
        c = hands[direction].get('C', '') or '-'
        result[direction] = f"{s}.{h}.{d}.{c}"
    return result


def update_hands(new_events=None):
    """Step 2: Update hands database for new or specified events"""
    log_section("STEP 2: UPDATING BOARD HANDS")
    
    # Load existing hands database
    try:
        with open(HANDS_DB_FILE, 'r', encoding='utf-8') as f:
            hands_db = json.load(f)
    except:
        hands_db = []
    
    log(f"Existing hands database: {len(hands_db)} records")
    
    # Create index by date and board
    hands_index = {}
    for hand in hands_db:
        key = f"{hand.get('date', '')}_{hand.get('board', '')}"
        hands_index[key] = hand
    
    # Get events to fetch
    if new_events:
        # Use provided events list
        events_to_fetch = new_events
        log(f"Fetching hands for {len(events_to_fetch)} new event(s)")
    else:
        # Get from calendar
        events_by_date = get_calendar_events()
        hands_dates = set(hand.get('date', '') for hand in hands_db)
        
        missing_dates = [d for d in events_by_date.keys() if d not in hands_dates]
        missing_dates.sort(key=lambda x: datetime.strptime(x, "%d.%m.%Y"))
        
        if not missing_dates:
            log("✓ Hands database is up to date!")
            return True, []
        
        events_to_fetch = []
        for d in missing_dates:
            if d in events_by_date and events_by_date[d]:
                events_to_fetch.append({
                    'id': events_by_date[d][0]['id'],
                    'date': d
                })
        
        log(f"Found {len(missing_dates)} date(s) needing hands")
    
    if not events_to_fetch:
        log("✓ No new events to fetch hands for")
        return True, []
    
    # Generate next ID
    max_id = 0
    for h in hands_db:
        hid = h.get('id')
        if isinstance(hid, int) and hid > max_id:
            max_id = hid
    next_id = max_id + 1
    
    new_hands = []
    
    for event in events_to_fetch:
        event_id = event['id']
        tarih = event['date']
        
        log(f"Fetching boards for {tarih} (Event {event_id})")
        boards_fetched = 0
        
        for board_num in range(1, BOARDS_PER_EVENT + 1):
            key = f"{tarih}_{board_num}"
            
            if key in hands_index:
                continue
            
            hands = fetch_board_hands(event_id, board_num)
            
            if hands:
                bbo_hands = format_hand_for_bbo(hands)
                
                new_record = {
                    'id': next_id,
                    'board': board_num,
                    'date': tarih,
                    'dealer': get_dealer_for_board(board_num),
                    'vulnerability': get_vulnerability_for_board(board_num),
                    'N': bbo_hands['N'],
                    'S': bbo_hands['S'],
                    'E': bbo_hands['E'],
                    'W': bbo_hands['W'],
                    'dd_analysis': None,
                    'optimum': None,
                    'lott': None
                }
                
                hands_db.append(new_record)
                hands_index[key] = new_record
                new_hands.append(new_record)
                next_id += 1
                boards_fetched += 1
            
            time.sleep(0.1)
        
        log(f"  {tarih}: {boards_fetched} boards fetched")
    
    if new_hands:
        # Sort by date and board
        def sort_key(h):
            tarih = h.get('date', '01.01.2000')
            parts = tarih.split('.')
            if len(parts) == 3:
                return (int(parts[2]), int(parts[1]), int(parts[0]), h.get('board', 0))
            return (0, 0, 0, 0)
        
        hands_db.sort(key=sort_key)
        
        try:
            with open(HANDS_DB_FILE, 'w', encoding='utf-8') as f:
                json.dump(hands_db, f, indent=2, ensure_ascii=False)
            log(f"✓ Hands database saved ({len(new_hands)} new hands)")
            return True, new_hands
        except Exception as e:
            log(f"✗ Failed to save hands database: {e}", "ERROR")
            return False, []
    
    return True, []


# ============================================================
# STEP 3: DD ANALYSIS (Double Dummy)
# ============================================================

def run_dd_analysis(new_hands=None, force=False):
    """Step 3: Run Double Dummy analysis on new hands"""
    log_section("STEP 3: RUNNING DD ANALYSIS")
    
    # Check if endplay is available
    try:
        from endplay.types import Deal, Player, Vul
        from endplay.dds import calc_dd_table, par
        log("endplay library loaded successfully")
        ENDPLAY_AVAILABLE = True
    except ImportError:
        log("UYARI: endplay kütüphanesi bulunamadı - DD analizi atlanıyor", "WARN")
        log("Kurulum: pip install endplay", "WARN")
        log("NOT: Railway deployment'ta bu adım otomatik çalışacaktır", "INFO")
        return True, 0  # Return success but 0 hands analyzed
    
    # Load hands database
    try:
        with open(HANDS_DB_FILE, 'r', encoding='utf-8') as f:
            hands_db = json.load(f)
    except Exception as e:
        log(f"Error loading hands database: {e}", "ERROR")
        return False, 0
    
    # Find hands needing analysis
    if force:
        # Analyze all hands
        hands_to_analyze = hands_db
        log(f"Force mode: Analyzing all {len(hands_to_analyze)} hands")
    elif new_hands:
        # Analyze only new hands
        new_ids = set(h.get('id') for h in new_hands)
        hands_to_analyze = [h for h in hands_db if h.get('id') in new_ids]
        log(f"Analyzing {len(hands_to_analyze)} new hands")
    else:
        # Analyze hands without DD data
        hands_to_analyze = [h for h in hands_db if not h.get('dd_analysis')]
        log(f"Found {len(hands_to_analyze)} hands without DD analysis")
    
    if not hands_to_analyze:
        log("✓ All hands have DD analysis!")
        return True, 0
    
    # DD analysis functions
    def hand_to_pbn(n, s, e, w, dealer='N'):
        if dealer == 'N':
            return f"N:{n} {e} {s} {w}"
        elif dealer == 'E':
            return f"E:{e} {s} {w} {n}"
        elif dealer == 'S':
            return f"S:{s} {w} {n} {e}"
        elif dealer == 'W':
            return f"W:{w} {n} {e} {s}"
        return f"N:{n} {e} {s} {w}"
    
    def get_vul_enum(vuln_str):
        vul_map = {
            'None': Vul.none, 'NS': Vul.ns, 'EW': Vul.ew, 'Both': Vul.both,
            'All': Vul.both, 'none': Vul.none, '-': Vul.none, 'Yok': Vul.none,
        }
        return vul_map.get(vuln_str, Vul.none)
    
    def get_dealer_enum(dealer_str):
        dealer_map = {'N': Player.north, 'E': Player.east, 'S': Player.south, 'W': Player.west}
        return dealer_map.get(dealer_str, Player.north)
    
    def parse_dd_table(table):
        result = {}
        table_str = str(table)
        parts = table_str.split(';')
        suits_order = ['C', 'D', 'H', 'S', 'NT']
        
        for part in parts[1:]:
            if ':' in part:
                pos, values = part.split(':')
                tricks = values.split(',')
                result[pos] = {}
                for i, suit in enumerate(suits_order):
                    if i < len(tricks):
                        result[pos][suit] = int(tricks[i])
        return result
    
    def format_optimum(par_result):
        if not par_result or par_result.score == 0:
            return {'text': 'Pass Out', 'score': 0, 'declarer': None, 'contract': None}
        
        contract = None
        for c in par_result:
            contract = c
            break
        
        if not contract:
            return {'text': f'Score: {par_result.score}', 'score': par_result.score, 'declarer': None, 'contract': None}
        
        contract_str = str(contract)
        side = 'NS' if ('N' in contract_str or 'S' in contract_str) else 'EW'
        level = contract.level
        
        denom_symbols = {'♣': '♣', '♦': '♦', '♥': '♥', '♠': '♠', 'N': 'NT'}
        denom_symbol = '?'
        for sym in denom_symbols:
            if sym in contract_str:
                denom_symbol = denom_symbols[sym]
                break
        
        overtricks = 0
        if '+' in contract_str:
            try:
                overtricks = int(contract_str.split('+')[1])
            except:
                pass
        
        total_tricks = level + 6 + overtricks
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
    
    def count_suit(hand, suit_index):
        parts = hand.split('.')
        if suit_index < len(parts):
            return len(parts[suit_index]) if parts[suit_index] != '-' else 0
        return 0
    
    def calculate_lott(dd_result, n_hand, s_hand, e_hand, w_hand):
        if not dd_result:
            return None
        
        suit_symbols = {'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣'}
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
    
    # Create ID to index mapping for updating
    id_to_index = {h.get('id'): i for i, h in enumerate(hands_db)}
    
    success_count = 0
    start_time = datetime.now()
    
    for i, hand in enumerate(hands_to_analyze):
        board_num = hand.get('board', '?')
        date = hand.get('date', 'Unknown')
        hand_id = hand.get('id')
        
        n = hand.get('N', '')
        s = hand.get('S', '')
        e = hand.get('E', '')
        w = hand.get('W', '')
        dealer = hand.get('dealer', 'N')
        vuln = hand.get('vulnerability', 'None')
        
        if not all([n, s, e, w]):
            log(f"  Board {board_num} ({date}): Missing hand data", "WARN")
            continue
        
        try:
            # Create PBN and Deal
            pbn = hand_to_pbn(n, s, e, w, dealer)
            deal = Deal(pbn)
            
            # Calculate DD table
            table = calc_dd_table(deal)
            
            # Calculate par score
            vul_enum = get_vul_enum(vuln)
            dealer_enum = get_dealer_enum(dealer)
            par_result = par(table, vul_enum, dealer_enum)
            
            # Format results
            dd_result = parse_dd_table(table)
            optimum = format_optimum(par_result)
            lott = calculate_lott(dd_result, n, s, e, w)
            
            # Update hands_db
            if hand_id in id_to_index:
                idx = id_to_index[hand_id]
                hands_db[idx]['dd_analysis'] = dd_result
                hands_db[idx]['optimum'] = optimum
                hands_db[idx]['lott'] = lott
            
            success_count += 1
            
            if (i + 1) % 10 == 0 or i == len(hands_to_analyze) - 1:
                log(f"  Progress: {i+1}/{len(hands_to_analyze)} ({success_count} successful)")
            
        except Exception as e:
            log(f"  Board {board_num} ({date}): DD error - {str(e)[:40]}", "ERROR")
    
    elapsed = (datetime.now() - start_time).total_seconds()
    
    # Save updated database
    if success_count > 0:
        try:
            with open(HANDS_DB_FILE, 'w', encoding='utf-8') as f:
                json.dump(hands_db, f, indent=2, ensure_ascii=False)
            log(f"✓ DD analysis completed: {success_count}/{len(hands_to_analyze)} hands ({elapsed:.1f}s)")
            return True, success_count
        except Exception as e:
            log(f"✗ Failed to save hands database: {e}", "ERROR")
            return False, success_count
    
    return True, 0


# ============================================================
# STEP 4: SITE ANALYSIS
# ============================================================

def run_site_analysis():
    """Step 4: Update site statistics and reports"""
    log_section("STEP 4: UPDATING SITE ANALYSIS")
    
    # Load databases
    try:
        with open(HANDS_DB_FILE, 'r', encoding='utf-8') as f:
            hands_db = json.load(f)
    except:
        hands_db = []
    
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            scores_db = json.load(f)
    except:
        scores_db = {}
    
    # Calculate statistics
    total_hands = len(hands_db)
    hands_with_dd = len([h for h in hands_db if h.get('dd_analysis')])
    
    unique_dates = set(h.get('date') for h in hands_db if h.get('date'))
    
    # LoTT statistics
    lott_values = [h.get('lott', {}).get('total_tricks') for h in hands_db if h.get('lott')]
    avg_lott = sum(lott_values) / len(lott_values) if lott_values else 0
    
    # Optimum contract distribution
    optimum_declarers = {'NS': 0, 'EW': 0, 'None': 0}
    for h in hands_db:
        opt = h.get('optimum', {})
        decl = opt.get('declarer') if opt else None
        if decl == 'NS':
            optimum_declarers['NS'] += 1
        elif decl == 'EW':
            optimum_declarers['EW'] += 1
        else:
            optimum_declarers['None'] += 1
    
    log(f"Statistics:")
    log(f"  Total hands: {total_hands}")
    log(f"  Hands with DD: {hands_with_dd}")
    log(f"  Unique dates: {len(unique_dates)}")
    log(f"  Average LoTT: {avg_lott:.2f}")
    log(f"  Optimum NS: {optimum_declarers['NS']}, EW: {optimum_declarers['EW']}, Pass: {optimum_declarers['None']}")
    
    # Update metadata in scores_db
    if isinstance(scores_db, dict):
        if 'metadata' not in scores_db:
            scores_db['metadata'] = {}
        
        scores_db['metadata'].update({
            'total_hands': total_hands,
            'hands_with_dd': hands_with_dd,
            'unique_tournament_dates': len(unique_dates),
            'average_lott': round(avg_lott, 2),
            'last_analysis_update': datetime.now().isoformat()
        })
        
        try:
            with open(DB_FILE, 'w', encoding='utf-8') as f:
                json.dump(scores_db, f, indent=2, ensure_ascii=False)
            log("✓ Site analysis metadata updated")
        except Exception as e:
            log(f"✗ Failed to save metadata: {e}", "ERROR")
    
    log("✓ Site analysis completed")
    return True


# ============================================================
# MAIN PIPELINE
# ============================================================

def run_full_pipeline(step=None, force=False):
    """Run the full update pipeline or a specific step"""
    
    log("\n" + "=" * 60)
    log("🚀 BRIC FULL UPDATE PIPELINE")
    log(f"Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 60)
    
    success = True
    new_events = []
    new_hands = []
    
    # Step 1: Scores
    if step is None or step == 'scores':
        score_success, new_events = update_scores()
        success = success and score_success
    
    # Step 2: Hands
    if step is None or step == 'hands':
        hands_success, new_hands = update_hands(new_events if step is None else None)
        success = success and hands_success
    
    # Step 3: DD Analysis
    if step is None or step == 'dd':
        dd_success, dd_count = run_dd_analysis(new_hands if step is None else None, force)
        success = success and dd_success
    
    # Step 4: Board Rankings
    if step is None or step == 'rankings':
        log_section("STEP 4: FETCHING BOARD RANKINGS")
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, 'fetch_missing_rankings.py', '--once'],
                capture_output=True,
                text=True,
                timeout=600
            )
            if result.returncode == 0:
                log("Board rankings updated successfully")
            else:
                log(f"Board rankings failed: {result.stderr}", "WARNING")
        except Exception as e:
            log(f"Board rankings error: {e}", "WARNING")
    
    # Step 5: Site Analysis
    if step is None or step == 'analysis':
        analysis_success = run_site_analysis()
        success = success and analysis_success
    
    log("\n" + "=" * 60)
    log(f"Pipeline completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"Status: {'✓ SUCCESS' if success else '✗ FAILED'}")
    log("=" * 60 + "\n")
    
    return success


def main():
    """Main entry point with argument parsing"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='BRIC Full Update Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python full_update_pipeline.py                  # Run full pipeline
  python full_update_pipeline.py --step scores    # Only update scores
  python full_update_pipeline.py --step hands     # Only fetch hands
  python full_update_pipeline.py --step dd        # Only run DD analysis
  python full_update_pipeline.py --step analysis  # Only update site analysis
  python full_update_pipeline.py --force          # Re-analyze all hands
        """
    )
    
    parser.add_argument(
        '--step',
        choices=['scores', 'hands', 'dd', 'analysis'],
        help='Run only a specific step of the pipeline'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force re-analysis of all hands (for DD step)'
    )
    
    args = parser.parse_args()
    
    success = run_full_pipeline(step=args.step, force=args.force)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
