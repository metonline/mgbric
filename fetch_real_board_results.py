#!/usr/bin/env python3
"""
Fetch real board results from vugraph and save to board_results.json
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

def parse_suit(text):
    """Convert suit codes to symbols"""
    text = text.replace('S', '♠').replace('H', '♥').replace('D', '♦').replace('C', '♣')
    return text

def fetch_pair_result(event_id, board_num, pair_num, direction, pair_names_dict=None):
    """Fetch result for a single pair on a board"""
    try:
        # Use the correct direction page for each pair type
        url = f'https://clubs.vugraph.com/hosgoru/boarddetails.php?event={event_id}&section=A&pair={pair_num}&direction={direction}&board={board_num}'
        resp = requests.get(url, timeout=15)
        resp.encoding = 'iso-8859-9'
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        if 'Page not Found' in resp.text or 'Sayfa Bulunamadı' in resp.text:
            return None
        
        # Get pair names from h3
        pair_names = ""
        h3 = soup.find('h3')
        if h3:
            h3_text = h3.get_text(strip=True)
            match = re.search(r'\d{2}:\d{2}\s*\.\.\.\s*(.+?)\s*\.\.\.\s*Bord', h3_text)
            if match:
                pair_names = match.group(1).strip()
        
        # Fallback to dict if h3 didn't work
        if not pair_names and pair_names_dict and pair_num in pair_names_dict:
            pair_names = pair_names_dict[pair_num]
        
        if not pair_names:
            return None
        
        # Find highlighted row (this pair's result)
        table = soup.find('table', class_='results')
        if not table:
            return None
        
        for row in table.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) >= 8:
                cell_class = cells[0].get('class', [''])[0] if cells[0].get('class') else ''
                if cell_class in ['fantastic', 'resultspecial', 'resultsimportant']:
                    contract = parse_suit(cells[0].get_text(strip=True))
                    if not contract or contract == '-6':
                        return None
                    
                    declarer = cells[1].get_text(strip=True)
                    result = cells[2].get_text(strip=True)
                    lead = parse_suit(cells[3].get_text(strip=True))
                    score_ns = cells[4].get_text(strip=True)
                    score_ew = cells[5].get_text(strip=True)
                    pct_ns_str = cells[6].get_text(strip=True)
                    pct_ew_str = cells[7].get_text(strip=True)
                    
                    # Parse percentages
                    try:
                        pct_ns = float(pct_ns_str) if pct_ns_str and pct_ns_str.replace('.','').isdigit() else 0
                    except:
                        pct_ns = 0
                    try:
                        pct_ew = float(pct_ew_str) if pct_ew_str and pct_ew_str.replace('.','').isdigit() else 0
                    except:
                        pct_ew = 100 - pct_ns  # fallback
                    
                    if direction == 'NS':
                        # NS pair: use NS score and NS percent
                        if score_ns:
                            score = int(score_ns) if score_ns.lstrip('-').isdigit() else 0
                        else:
                            score = -int(score_ew) if score_ew.lstrip('-').isdigit() else 0
                        percent = pct_ns
                    else:
                        # EW pair: use EW score and EW percent = 100 - NS percent
                        if score_ew:
                            score = int(score_ew) if score_ew.lstrip('-').isdigit() else 0
                        else:
                            score = -int(score_ns) if score_ns.lstrip('-').isdigit() else 0
                        percent = round(100 - pct_ns, 2)
                    
                    return {
                        'pair_names': pair_names,
                        'direction': direction,
                        'contract': contract,
                        'declarer': declarer,
                        'result': result,
                        'lead': lead,
                        'score': score,
                        'percent': percent
                    }
        return None
    except Exception as e:
        return None

def fetch_event_info(event_id):
    """Fetch event name, date and pair names"""
    url = f'https://clubs.vugraph.com/hosgoru/eventresults.php?event={event_id}'
    resp = requests.get(url, timeout=15)
    resp.encoding = 'iso-8859-9'
    soup = BeautifulSoup(resp.content, 'html.parser')
    
    name = ""
    date = ""
    h3 = soup.find('h3')
    if h3:
        h3_text = h3.get_text(strip=True)
        date_match = re.search(r'(\d{2})-(\d{2})-(\d{4})', h3_text)
        if date_match:
            day, month, year = date_match.groups()
            date = f"{day}.{month}.{year}"
        parts = h3_text.split()
        if parts:
            name = parts[0]
    
    # Get NS and EW pair counts and names
    ns_pairs = {}
    ew_pairs = {}
    table = soup.find('table', class_='colored')
    if table:
        rows = table.find_all('tr')
        in_ns = False
        in_ew = False
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if not cells:
                continue
            first_text = cells[0].get_text(strip=True)
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
            if len(cells) >= 2 and first_text.isdigit():
                pair_num = int(first_text)
                pair_name = cells[1].get_text(strip=True)
                if in_ns:
                    ns_pairs[pair_num] = pair_name
                elif in_ew:
                    ew_pairs[pair_num] = pair_name
    
    return {
        'name': name, 
        'date': date,
        'ns_pairs': len(ns_pairs) if ns_pairs else 13,
        'ew_pairs': len(ew_pairs) if ew_pairs else 13,
        'ns_pair_names': ns_pairs,
        'ew_pair_names': ew_pairs
    }

def fetch_board_all_results(event_id, board_num, ns_pair_names=None, ew_pair_names=None):
    """Fetch all results for a board from a single page - both NS and EW"""
    try:
        # Use NS pair 1's page to get all results
        url = f'https://clubs.vugraph.com/hosgoru/boarddetails.php?event={event_id}&section=A&pair=1&direction=NS&board={board_num}'
        resp = requests.get(url, timeout=15)
        resp.encoding = 'iso-8859-9'
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        if 'Page not Found' in resp.text or 'Sayfa Bulunamadı' in resp.text:
            return []
        
        results = []
        table = soup.find('table', class_='results')
        if not table:
            return []
        
        rows = table.find_all('tr')[1:]  # Skip header
        
        for row_idx, row in enumerate(rows):
            cells = row.find_all('td')
            if len(cells) >= 8:
                contract = parse_suit(cells[0].get_text(strip=True))
                if not contract or contract == '-6':
                    continue
                
                declarer = cells[1].get_text(strip=True)
                result = cells[2].get_text(strip=True)
                lead = parse_suit(cells[3].get_text(strip=True))
                score_ns = cells[4].get_text(strip=True)
                score_ew = cells[5].get_text(strip=True)
                pct_ns_str = cells[6].get_text(strip=True)
                pct_ew_str = cells[7].get_text(strip=True)
                
                # Parse percentages
                try:
                    pct_ns = float(pct_ns_str) if pct_ns_str and pct_ns_str.replace('.','').isdigit() else 0
                except:
                    pct_ns = 0
                
                # EW percent = 100 - NS percent
                pct_ew = round(100 - pct_ns, 2)
                
                # Parse scores
                ns_score = 0
                ew_score = 0
                if score_ns:
                    ns_score = int(score_ns) if score_ns.lstrip('-').isdigit() else 0
                    ew_score = -ns_score
                elif score_ew:
                    ew_score = int(score_ew) if score_ew.lstrip('-').isdigit() else 0
                    ns_score = -ew_score
                
                # Get pair names from dict using row index + 1 as pair number
                pair_num = row_idx + 1
                ns_name = ns_pair_names.get(pair_num, f"NS Pair {pair_num}") if ns_pair_names else f"NS Pair {pair_num}"
                ew_name = ew_pair_names.get(pair_num, f"EW Pair {pair_num}") if ew_pair_names else f"EW Pair {pair_num}"
                
                # Add NS result
                results.append({
                    'pair_names': ns_name,
                    'direction': 'NS',
                    'contract': contract,
                    'declarer': declarer,
                    'result': result,
                    'lead': lead,
                    'score': ns_score,
                    'percent': pct_ns
                })
                
                # Add EW result
                results.append({
                    'pair_names': ew_name,
                    'direction': 'EW',
                    'contract': contract,
                    'declarer': declarer,
                    'result': result,
                    'lead': lead,
                    'score': ew_score,
                    'percent': pct_ew
                })
        
        # Sort by percent and assign ranks
        results.sort(key=lambda x: x['percent'], reverse=True)
        for i, r in enumerate(results, 1):
            r['rank'] = i
        
        return results
    except Exception as e:
        print(f"Error: {e}")
        return []

def fetch_board_results(event_id, board_num, ns_count, ew_count, ns_pair_names=None, ew_pair_names=None):
    """Fetch all results for a board - NS pairs from NS pages, EW from same page with 100-NS%"""
    all_results = []
    ns_results = []
    
    # First, fetch NS pairs from NS direction pages
    tasks = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        for pair_num in range(1, ns_count + 1):
            tasks.append(executor.submit(fetch_pair_result, event_id, board_num, pair_num, 'NS', ns_pair_names))
        
        for future in as_completed(tasks):
            result = future.result()
            if result:
                ns_results.append(result)
    
    all_results.extend(ns_results)
    
    # Now create EW results: for each NS result, create corresponding EW result
    # EW pair names come from ew_pair_names dict
    for idx, ns_res in enumerate(ns_results):
        pair_num = idx + 1
        ew_name = ew_pair_names.get(pair_num, f"EW Pair {pair_num}") if ew_pair_names else f"EW Pair {pair_num}"
        
        # EW score is negative of NS score, EW percent = 100 - NS percent
        ew_result = {
            'pair_names': ew_name,
            'direction': 'EW',
            'contract': ns_res['contract'],
            'declarer': ns_res['declarer'],
            'result': ns_res['result'],
            'lead': ns_res['lead'],
            'score': -ns_res['score'],
            'percent': round(100 - ns_res['percent'], 2)
        }
        all_results.append(ew_result)
    
    # Sort by percent and assign ranks
    all_results.sort(key=lambda x: x['percent'], reverse=True)
    for i, r in enumerate(all_results, 1):
        r['rank'] = i
    
    return all_results

def fetch_all_boards_for_event(event_id, max_boards=30):
    """Fetch all board results for an event"""
    print(f"Fetching event {event_id}...")
    event_info = fetch_event_info(event_id)
    print(f"  Event: {event_info['name']} - {event_info['date']}")
    print(f"  NS pairs: {event_info['ns_pairs']}, EW pairs: {event_info['ew_pairs']}")
    
    boards = {}
    for board_num in range(1, max_boards + 1):
        results = fetch_board_results(
            event_id, board_num, 
            event_info['ns_pairs'], event_info['ew_pairs'],
            event_info.get('ns_pair_names'), event_info.get('ew_pair_names')
        )
        if results:
            board_key = f"{event_id}_{board_num}"
            boards[board_key] = {'results': results}
            print(f"  Board {board_num}: {len(results)} results")
        else:
            print(f"  Board {board_num}: No results")
    
    return event_info, boards

def main():
    """Fetch board rankings for all events"""
    import sys
    
    # Check for command line args
    if len(sys.argv) > 1 and sys.argv[1] == '--single':
        # Single event mode (for testing)
        event_id = sys.argv[2] if len(sys.argv) > 2 else '404155'
        event_info, boards = fetch_all_boards_for_event(event_id)
        
        output = {
            'boards': boards,
            'events': {event_id: event_info},
            'updated_at': datetime.now().isoformat()
        }
        
        with open('board_results.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\nSaved {len(boards)} boards to board_results.json")
        return
    
    # Full mode - fetch all events from event_registry
    try:
        from event_registry import EventRegistry
        registry = EventRegistry()
        all_events = registry.get_all_events()  # {date: event_id}
        print(f"Found {len(all_events)} events in registry")
    except Exception as e:
        print(f"Error loading registry: {e}")
        # Fallback to database.json
        try:
            with open('database.json', 'r', encoding='utf-8') as f:
                db = json.load(f)
            all_events = {}
            for key, ev in db.get('events', {}).items():
                event_id = ev.get('id')
                date = ev.get('date')
                if event_id and date:
                    all_events[date] = event_id
            print(f"Found {len(all_events)} events in database.json")
        except:
            print("No events found!")
            return
    
    # Load existing board_results to preserve data
    existing_data = {'boards': {}, 'events': {}}
    try:
        with open('board_results.json', 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        print(f"Loaded existing data: {len(existing_data.get('boards', {}))} boards")
    except:
        pass
    
    output = {
        'boards': existing_data.get('boards', {}),
        'events': existing_data.get('events', {}),
        'updated_at': datetime.now().isoformat()
    }
    
    total_new_boards = 0
    
    # Process each event (only 2026)
    for date, event_id in sorted(all_events.items(), reverse=True):
        # Only process 2026 events
        if not date or '2026' not in date:
            continue
            
        # Check if we already have data for this event
        existing_boards = [k for k in output['boards'].keys() if k.startswith(f"{event_id}_")]
        if len(existing_boards) >= 20:  # Already have most boards
            print(f"[SKIP] Event {event_id} ({date}) - already have {len(existing_boards)} boards")
            continue
        
        print(f"\n{'='*60}")
        print(f"Processing Event {event_id} ({date})")
        
        try:
            event_info, boards = fetch_all_boards_for_event(event_id)
            
            # Merge with existing
            for board_key, board_data in boards.items():
                output['boards'][board_key] = board_data
                total_new_boards += 1
            
            output['events'][event_id] = event_info
            
            # Save after each event
            output['updated_at'] = datetime.now().isoformat()
            with open('board_results.json', 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            
            print(f"  Saved {len(boards)} boards for event {event_id}")
            
        except Exception as e:
            print(f"  Error processing event {event_id}: {e}")
            continue
    
    print(f"\n{'='*60}")
    print(f"COMPLETED!")
    print(f"Total events: {len(output['events'])}")
    print(f"Total boards: {len(output['boards'])}")
    print(f"New boards added: {total_new_boards}")

if __name__ == '__main__':
    main()
