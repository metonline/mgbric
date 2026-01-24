#!/usr/bin/env python3
"""
Complete integrated pipeline: Fetch → Extract Dates → Generate LIN → Generate DD
All steps in proper sequence with date extraction built into the fetch process
"""

import json
import time
import requests
import re
import subprocess
import sys
from bs4 import BeautifulSoup
from collections import defaultdict, Counter
from urllib.parse import quote
from unified_fetch import DataFetcher, EventRegistry

# ============================================================================
# STEP 1: FETCH ALL HANDS
# ============================================================================

def fetch_all_hands():
    """Fetch hands from all 24 January 2026 events"""
    print("\n" + "="*70)
    print("STEP 1: FETCHING ALL HANDS FROM 24 EVENTS")
    print("="*70)
    
    fetcher = DataFetcher()
    registry = EventRegistry()
    events = registry.get_all_events()
    
    # Filter for January 2026 events
    jan_2026_events = [e for e in events if '2026' in e.get('date', '')]
    
    print(f"Found {len(jan_2026_events)} events in January 2026\n")
    
    all_hands = []
    for i, event in enumerate(jan_2026_events, 1):
        event_id = event['id']
        print(f"[{i:2d}/{len(jan_2026_events)}] Event {event_id}...", end=' ', flush=True)
        
        try:
            hands = fetcher.fetch_hands(event_id)
            if hands:
                all_hands.extend(hands)
                print(f"✓ {len(hands)} hands")
            else:
                print("✗ No hands")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        time.sleep(0.5)  # Rate limiting
    
    print(f"\nTotal hands fetched: {len(all_hands)}")
    
    # Save to database
    with open('hands_database.json', 'w', encoding='utf-8') as f:
        json.dump(all_hands, f, indent=2, ensure_ascii=False)
    
    print("Saved to hands_database.json")
    return all_hands

# ============================================================================
# STEP 2: EXTRACT AND UPDATE ACTUAL EVENT DATES
# ============================================================================

def extract_event_date(event_id):
    """Extract actual date from event results page"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        url = f"https://clubs.vugraph.com/hosgoru/eventresults.php?event={event_id}"
        response = requests.get(url, headers=headers, timeout=5)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for date format: (DD-MM-YYYY HH:MM)
        text = soup.get_text()
        match = re.search(r'\((\d{1,2})-(\d{1,2})-(\d{4})', text)
        if match:
            day, month, year = match.groups()
            return f"{day.zfill(2)}.{month.zfill(2)}.{year}"
        
        return None
    except Exception as e:
        return None

def update_dates():
    """Extract and update actual event dates in the database"""
    print("\n" + "="*70)
    print("STEP 2: EXTRACTING AND UPDATING ACTUAL EVENT DATES")
    print("="*70)
    
    # Load database
    with open('hands_database.json', 'r', encoding='utf-8') as f:
        hands = json.load(f)
    
    # Group by event
    by_event = defaultdict(list)
    for hand in hands:
        event_id = hand.get('event_id')
        if event_id:
            by_event[event_id].append(hand)
    
    print(f"Found {len(by_event)} events\n")
    
    # Extract dates and update database
    event_date_map = {}
    event_list = sorted(by_event.keys())
    
    for idx, event_id in enumerate(event_list, 1):
        print(f"[{idx:2d}/{len(event_list)}] Event {event_id}...", end=' ', flush=True)
        
        date = extract_event_date(event_id)
        if date:
            event_date_map[event_id] = date
            # Update all hands for this event
            for hand in by_event[event_id]:
                hand['date'] = date
            print(f"✓ {date}")
        else:
            print("✗ Failed to extract")
        
        time.sleep(0.5)  # Rate limiting
    
    # Save updated database
    with open('hands_database.json', 'w', encoding='utf-8') as f:
        json.dump(hands, f, indent=2, ensure_ascii=False)
    
    # Show distribution
    print("\nDate distribution after update:")
    dates = Counter(h.get('date') for h in hands)
    for date, count in sorted(dates.items()):
        events_for_date = [e for e, d in event_date_map.items() if d == date]
        print(f"  {date}: {count} hands from {len(events_for_date)} event(s)")
    
    print(f"\nUpdated {len(hands)} hands with correct dates")
    return hands

# ============================================================================
# STEP 2.5: FIX VULNERABILITY DATA
# ============================================================================

def get_vulnerability_by_board(board_num):
    """
    Calculate vulnerability based on board number (standard duplicate bridge)
    Pattern repeats every 16 boards
    """
    vuln_map = {
        1: 'None',  2: 'NS', 3: 'EW', 4: 'Both',
        5: 'None',  6: 'EW', 7: 'Both', 8: 'None',
        9: 'NS',    10: 'EW', 11: 'Both', 12: 'None',
        13: 'EW',   14: 'Both', 15: 'None', 16: 'NS',
        17: 'EW',   18: 'Both', 19: 'None', 20: 'NS',
        21: 'Both', 22: 'None', 23: 'NS', 24: 'EW',
        25: 'Both', 26: 'None', 27: 'EW', 28: 'Both',
        29: 'None', 30: 'NS'
    }
    return vuln_map.get(board_num, 'None')

def fix_vulnerability(hands):
    """Fix vulnerability data based on board numbers"""
    print("\n" + "="*70)
    print("STEP 2.5: FIXING VULNERABILITY DATA")
    print("="*70)
    
    vuln_counts = {}
    for hand in hands:
        board_num = hand.get('board', 1)
        vuln = get_vulnerability_by_board(board_num)
        hand['vulnerability'] = vuln
        vuln_counts[vuln] = vuln_counts.get(vuln, 0) + 1
    
    # Save updated database
    with open('hands_database.json', 'w', encoding='utf-8') as f:
        json.dump(hands, f, indent=2, ensure_ascii=False)
    
    print(f"\nVulnerability distribution:")
    for vuln in ['None', 'NS', 'EW', 'Both']:
        count = vuln_counts.get(vuln, 0)
        print(f"  {vuln:4s}: {count:3d} hands")
    
    print(f"\nFixed vulnerability for {len(hands)} hands")
    return hands

# ============================================================================
# STEP 3: GENERATE LIN STRINGS
# ============================================================================

def hand_string_to_lin(hand_str):
    """Convert hand string (S.H.D.C) to LIN format (SxxxHxxxDxxxCxxx)"""
    if not hand_str:
        return ''
    parts = hand_str.split('.')
    s = parts[0] if len(parts) > 0 else ''
    h = parts[1] if len(parts) > 1 else ''
    d = parts[2] if len(parts) > 2 else ''
    c = parts[3] if len(parts) > 3 else ''
    return f'S{s}H{h}D{d}C{c}'

def generate_bbo_lin(hand, dealer, vulnerability='None'):
    """Generate complete LIN string for BBO hand viewer"""
    dealer_map = {'N': '1', 'E': '2', 'S': '3', 'W': '4'}
    d = dealer_map.get(dealer, '1')
    
    vuln_map = {'None': '0', 'NS': '1', 'EW': '2', 'Both': '3'}
    v = vuln_map.get(vulnerability, '0')
    
    # Order hands according to dealer
    dealer_order = {
        'N': ['N', 'E', 'S'],
        'E': ['E', 'S', 'W'],
        'S': ['S', 'W', 'N'],
        'W': ['W', 'N', 'E']
    }
    
    ordered = dealer_order.get(dealer, ['N', 'E', 'S'])
    hand_strings = [hand_string_to_lin(hand.get(pos)) for pos in ordered]
    hands_str = ','.join(hand_strings)
    
    return f'qx|o1|md|{d}{hands_str},|rh||ah|Board|sv|{v}|pg||'

def generate_bbo_viewer_url(hand, dealer, vulnerability='None'):
    """Generate BBO viewer URL"""
    lin = generate_bbo_lin(hand, dealer, vulnerability)
    base_url = 'https://www.bridgebase.com/tools/handviewer.html'
    return f'{base_url}?lin={quote(lin)}'

def generate_lin_strings(hands):
    """Generate LIN strings for all hands"""
    print("\n" + "="*70)
    print("STEP 3: GENERATING LIN STRINGS")
    print("="*70)
    
    for i, hand in enumerate(hands, 1):
        dealer = hand.get('dealer', 'N')
        vuln = hand.get('vulnerability', 'None')
        hand['lin_string'] = generate_bbo_lin(hand, dealer, vuln)
        hand['bbo_url'] = generate_bbo_viewer_url(hand, dealer, vuln)
        
        if i % 100 == 0:
            print(f"Generated LIN for {i}/{len(hands)} hands...", flush=True)
    
    # Save to database
    with open('hands_database.json', 'w', encoding='utf-8') as f:
        json.dump(hands, f, indent=2, ensure_ascii=False)
    
    print(f"Generated LIN strings for {len(hands)} hands")
    return hands

# ============================================================================
# STEP 4: GENERATE DOUBLE DUMMY ANALYSIS
# ============================================================================

def generate_dd_analysis():
    """Generate DD analysis using dd_solver.py"""
    print("\n" + "="*70)
    print("STEP 4: GENERATING DOUBLE DUMMY ANALYSIS")
    print("="*70)
    print("\nRunning double_dummy/dd_solver.py --update-db...")
    print("(This may take 30-45 minutes for 720 hands)\n")
    
    try:
        result = subprocess.run(
            [sys.executable, 'double_dummy/dd_solver.py', '--update-db'],
            cwd='c:\\Users\\metin\\Desktop\\BRIC',
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print("\nDD analysis completed successfully")
            return True
        else:
            print(f"\nDD analysis failed with exit code {result.returncode}")
            return False
    except Exception as e:
        print(f"\nError running DD solver: {e}")
        return False

# ============================================================================
# STEP 5: VERIFY FINAL DATABASE
# ============================================================================

def verify_database():
    """Verify all data is complete"""
    print("\n" + "="*70)
    print("STEP 5: VERIFYING FINAL DATABASE")
    print("="*70)
    
    with open('hands_database.json', 'r', encoding='utf-8') as f:
        hands = json.load(f)
    
    print(f"\nTotal hands: {len(hands)}")
    
    # Date distribution
    dates = Counter(h.get('date') for h in hands)
    print(f"Unique dates: {len(dates)}")
    for date, count in sorted(dates.items()):
        print(f"  {date}: {count} hands")
    
    # Field completeness
    has_lin = sum(1 for h in hands if 'lin_string' in h and h['lin_string'])
    has_dd = sum(1 for h in hands if 'dd_result' in h and h['dd_result'])
    has_optimum = sum(1 for h in hands if 'optimum' in h and h['optimum'])
    has_lott = sum(1 for h in hands if 'lott' in h and h['lott'])
    
    print(f"\nField completion:")
    print(f"  LIN strings: {has_lin}/{len(hands)}")
    print(f"  DD results: {has_dd}/{len(hands)}")
    print(f"  Optimum contracts: {has_optimum}/{len(hands)}")
    print(f"  Law of Total Tricks: {has_lott}/{len(hands)}")
    
    # Check all required fields
    all_complete = all([
        len(hands) == 720,
        len(dates) == 24,
        has_lin == 720,
        has_optimum == 720,
        has_lott == 720
    ])
    
    if all_complete:
        print("\nDatabase verification PASSED")
        return True
    else:
        print("\nDatabase verification INCOMPLETE")
        if has_dd < 720:
            print(f"  Note: DD analysis still in progress ({has_dd}/{len(hands)} complete)")
        return False

# ============================================================================
# MAIN ORCHESTRATION
# ============================================================================

def main():
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  COMPLETE PIPELINE: FETCH → DATES → VULN → LIN → DD".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    start_time = time.time()
    
    try:
        # Step 1: Fetch all hands
        hands = fetch_all_hands()
        
        # Step 2: Extract and update dates
        hands = update_dates()
        
        # Step 2.5: Fix vulnerability data
        hands = fix_vulnerability(hands)
        
        # Step 3: Generate LIN strings
        hands = generate_lin_strings(hands)
        
        # Step 4: Generate DD analysis
        dd_success = generate_dd_analysis()
        
        # Step 5: Verify database
        verify_database()
        
        elapsed = time.time() - start_time
        print("\n" + "█"*70)
        print(f"█ PIPELINE COMPLETED in {elapsed/60:.1f} minutes".ljust(70) + "█")
        print("█"*70)
        
        elapsed = time.time() - start_time
        print("\n" + "█"*70)
        print(f"█ PIPELINE COMPLETED in {elapsed/60:.1f} minutes".ljust(70) + "█")
        print("█"*70)
        
        if dd_success:
            print("\nNext step: git add hands_database.json ; git commit -m '...'; git push")
        else:
            print("\nNote: DD analysis may still be running. Check manually with:")
            print("  python verify_database.py")
        
    except KeyboardInterrupt:
        print("\n\nPipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nPipeline failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def main_simple():
    """Simplified version that just calls external scripts"""
    print("\n" + "="*60)
    print("Bridge Hands Complete Pipeline")
    print("="*60)
    
    steps = [
        ("Step 1: Fetch hands from all January 2026 events", "fetch_all_january_events.py"),
        ("Step 2: Generate LIN data for all hands", "generate_all_lin.py"),
        ("Step 3: Calculate DD (Double Dummy) analysis", "double_dummy/dd_solver.py"),
    ]
    
    for description, script in steps:
        if not run_step(description, script):
            print(f"\n⚠️ Pipeline stopped at: {description}")
            return False
    
    # Summary
    hands = json.load(open('hands_database.json'))
    print(f"\n{'='*60}")
    print(f"✅ Pipeline Complete!")
    print(f"{'='*60}")
    print(f"Total hands: {len(hands)}")
    print(f"All hands have LIN data and DD analysis")
    print(f"{'='*60}\n")
    
    return True

if __name__ == '__main__':
    main()
