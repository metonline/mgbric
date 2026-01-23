#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scheduled Database Update Script for BRIC
Fetches new tournament scores and board hands from Vugraph
Can be run manually or scheduled via Windows Task Scheduler
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

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "https://clubs.vugraph.com/hosgoru"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(SCRIPT_DIR, 'database.json')
HANDS_DB_FILE = os.path.join(SCRIPT_DIR, 'hands_database.json')
LOG_FILE = os.path.join(SCRIPT_DIR, 'update_log.txt')


def log(message):
    """Log message to console and file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_msg + '\n')


def get_calendar_events():
    """
    Fetch calendar and extract all events with their dates and IDs
    Returns: dict mapping date strings to list of events
    """
    try:
        response = requests.get(f"{BASE_URL}/calendar.php", timeout=30)
        response.encoding = 'utf-8'
        response.raise_for_status()
    except Exception as e:
        log(f"Error fetching calendar: {e}")
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


def get_database_dates():
    """Get list of dates already in database"""
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        log(f"Error loading database: {e}")
        return set()
    
    dates = set()
    
    if isinstance(data, dict) and 'events' in data:
        # New format
        for event_data in data.get('events', {}).values():
            tarih = event_data.get('date')
            if tarih:
                dates.add(tarih)
        for record in data.get('legacy_records', []):
            tarih = record.get('Tarih')
            if tarih:
                dates.add(tarih)
    elif isinstance(data, list):
        # Old format
        for record in data:
            tarih = record.get('Tarih')
            if tarih:
                dates.add(tarih)
    
    return dates


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
        log(f"Error fetching event {event_id}: {e}")
        return []


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


def format_hand_for_bbo(hands):
    """Convert extracted hands to BBO viewer format"""
    result = {}
    for direction in ['N', 'S', 'E', 'W']:
        spades = hands[direction].get('S', '')
        hearts = hands[direction].get('H', '')
        diamonds = hands[direction].get('D', '')
        clubs = hands[direction].get('C', '')
        result[direction] = f"{spades}.{hearts}.{diamonds}.{clubs}"
    return result


def update_scores():
    """Update tournament scores database"""
    log("=" * 60)
    log("Updating tournament scores...")
    log("=" * 60)
    
    # Get calendar events
    events_by_date = get_calendar_events()
    log(f"Found {len(events_by_date)} dates with events in calendar")
    
    # Get existing dates
    db_dates = get_database_dates()
    log(f"Database has {len(db_dates)} unique dates")
    
    # Find missing dates
    missing_dates = [d for d in events_by_date.keys() if d not in db_dates]
    missing_dates.sort(key=lambda x: datetime.strptime(x, "%d.%m.%Y"))
    
    if not missing_dates:
        log("✓ Score database is up to date!")
        return True
    
    log(f"Found {len(missing_dates)} new date(s) to fetch: {missing_dates}")
    
    # Load current database
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        data = []
    
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
        log(f"✓ Score database saved successfully")
        return True
    except Exception as e:
        log(f"✗ Failed to save database: {e}")
        return False


def update_hands():
    """Update hands database for new events"""
    log("=" * 60)
    log("Updating board hands...")
    log("=" * 60)
    
    # Get calendar events
    events_by_date = get_calendar_events()
    
    # Load existing hands database
    try:
        with open(HANDS_DB_FILE, 'r', encoding='utf-8') as f:
            hands_db = json.load(f)
    except:
        hands_db = []
    
    # Create index by date and board
    hands_index = {}
    for hand in hands_db:
        key = f"{hand.get('Tarih', '')}_{hand.get('Board', '')}"
        hands_index[key] = hand
    
    # Get dates already in hands database
    hands_dates = set(hand.get('Tarih', '') for hand in hands_db)
    
    # Find dates that need hands fetched
    missing_dates = [d for d in events_by_date.keys() if d not in hands_dates]
    missing_dates.sort(key=lambda x: datetime.strptime(x, "%d.%m.%Y"))
    
    if not missing_dates:
        log("✓ Hands database is up to date!")
        return True
    
    log(f"Found {len(missing_dates)} date(s) needing hands: {missing_dates}")
    
    total_updated = 0
    
    for tarih in missing_dates:
        events = events_by_date.get(tarih, [])
        if not events:
            continue
        
        event_id = events[0]['id']  # Use first event for the date
        log(f"Fetching boards for {tarih} (Event {event_id})")
        
        for board_num in range(1, 31):
            key = f"{tarih}_{board_num}"
            
            if key in hands_index:
                continue
            
            hands = fetch_board_hands(event_id, board_num)
            
            if hands:
                bbo_hands = format_hand_for_bbo(hands)
                
                new_record = {
                    'Tarih': tarih,
                    'Board': board_num,
                    'N': bbo_hands['N'],
                    'S': bbo_hands['S'],
                    'E': bbo_hands['E'],
                    'W': bbo_hands['W'],
                    'Dealer': '',
                    'Vuln': ''
                }
                hands_db.append(new_record)
                hands_index[key] = new_record
                total_updated += 1
            
            time.sleep(0.1)
        
        log(f"  {tarih}: fetched boards")
    
    if total_updated > 0:
        # Sort by date and board
        def sort_key(h):
            tarih = h.get('Tarih', '01.01.2000')
            parts = tarih.split('.')
            if len(parts) == 3:
                return (int(parts[2]), int(parts[1]), int(parts[0]), h.get('Board', 0))
            return (0, 0, 0, 0)
        
        hands_db.sort(key=sort_key)
        
        try:
            with open(HANDS_DB_FILE, 'w', encoding='utf-8') as f:
                json.dump(hands_db, f, indent=2, ensure_ascii=False)
            log(f"✓ Hands database saved ({total_updated} boards added)")
            return True
        except Exception as e:
            log(f"✗ Failed to save hands database: {e}")
            return False
    
    return True


def main():
    """Main entry point"""
    log("\n" + "=" * 60)
    log("BRIC DATABASE UPDATE")
    log(f"Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 60)
    
    # Check command line args
    update_scores_flag = True
    update_hands_flag = True
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--scores-only':
            update_hands_flag = False
        elif sys.argv[1] == '--hands-only':
            update_scores_flag = False
        elif sys.argv[1] == '--help':
            print("Usage: python scheduled_update.py [OPTIONS]")
            print("Options:")
            print("  --scores-only  Update only tournament scores")
            print("  --hands-only   Update only board hands")
            print("  --help         Show this help message")
            return 0
    
    success = True
    
    if update_scores_flag:
        if not update_scores():
            success = False
    
    if update_hands_flag:
        if not update_hands():
            success = False
    
    log("\n" + "=" * 60)
    log(f"Update completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 60 + "\n")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
