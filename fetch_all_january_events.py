#!/usr/bin/env python3
"""Fetch hands ONLY from events in 2026 onwards (ignore historical data before 2026)"""

import json
import time
import requests
from bs4 import BeautifulSoup
from unified_fetch import DataFetcher, EventRegistry

def is_event_from_2026_or_later(date_str):
    """Check if event date is from 2026 or later"""
    if not date_str or date_str == 'unknown':
        return False
    try:
        # Parse date format: "23.01.2026" or similar
        parts = date_str.split('.')
        if len(parts) == 3:
            year = int(parts[2])
            return year >= 2026
    except:
        return False
    return False

def is_hand_from_2026_or_later(hand):
    """Check if hand is from 2026 or later"""
    return is_event_from_2026_or_later(hand.get('date', ''))

def fetch_calendar_events(month=1, year=2026):
    """Crawl vugraph calendar page to get fresh event list for a specific month
    
    Returns: {event_id: date_string} with dates extracted from calendar
    """
    try:
        url = f"https://clubs.vugraph.com/hosgoru/calendar.php?month={month}&year={year}"
        print(f"Crawling calendar: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"  ✗ Failed to fetch calendar (status: {response.status_code})")
            return {}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        events = {}
        import re
        
        # The calendar page has event links mixed throughout the HTML
        # Simply extract all event IDs and assign them the month/year
        # (We can't determine exact day from this calendar structure easily)
        
        # Find all links with event IDs
        # Links are in format: eventresults.php?event=405659
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Extract event ID from eventresults.php?event=XXXXX
            event_match = re.search(r'event=(\d+)', href)
            if not event_match:
                continue
            
            event_id = int(event_match.group(1))
            
            # For now, use first day of month as placeholder
            # The actual dates will come from fetching the event pages
            # or from registry fallback
            date_str = f"01.{month:02d}.{year}"
            
            # Only add if not already added
            if event_id not in events:
                events[event_id] = date_str
        
        print(f"  Found {len(events)} events in calendar for {month}/{year}")
        return events
        
    except Exception as e:
        print(f"  ✗ Error fetching calendar: {e}")
        return {}

def get_events_to_fetch():
    """Get events from 2026 onwards that need hands fetched
    
    First checks vugraph calendar for fresh event list with dates, then falls back to registry
    """
    fetcher = DataFetcher()
    
    # STEP 1: Try to fetch fresh event list from vugraph calendar
    print("\n📅 STEP 1: Checking vugraph calendar for new events...")
    calendar_events = {}  # {event_id: date_string}
    
    # Check multiple months (focusing on 2026)
    for year in [2026]:
        for month in [1, 2, 3]:  # Check Jan, Feb, Mar
            month_events = fetch_calendar_events(month, year)
            calendar_events.update(month_events)
            time.sleep(0.5)  # Be respectful to the server
    
    print(f"   Total events from calendar crawl: {len(calendar_events)}\n")
    
    # STEP 2: Fall back to registry for comprehensive event list
    print("📅 STEP 2: Loading registry as fallback...")
    registry = EventRegistry()
    registry_dict = registry.get_all_events()  # Returns {date: event_id}
    
    # Reverse to get {event_id: date}
    registry_events = {str(v): k for k, v in registry_dict.items()}
    
    print(f"   Total events from registry: {len(registry_events)}\n")
    
    # Combine both sources
    all_events_with_dates = {}
    all_events_with_dates.update(registry_events)  # Registry as base
    all_events_with_dates.update(calendar_events)  # Calendar overwrites (fresher data)
    
    # Filter to only 2026+ events
    events_2026_plus = {
        int(eid): date_str
        for eid, date_str in all_events_with_dates.items()
        if str(eid).isdigit() and is_event_from_2026_or_later(date_str)
    }
    
    print(f"✓ Total 2026+ events: {len(events_2026_plus)}\n")
    
    # Build a set of existing (event_id, board) tuples to skip duplicates
    existing_hands = set(
        (h.get('event_id'), h.get('board')) 
        for h in fetcher.hands 
        if h.get('event_id') and h.get('board')
    )
    
    # Get events already in database
    fetched_events = set(int(h.get('event_id', 0)) for h in fetcher.hands if h.get('event_id'))
    
    # Return events not yet fetched, sorted, plus the existing hands set and event dates
    unfetched = sorted([e for e in events_2026_plus.keys() if e not in fetched_events])
    
    # Also store event_dates for later use
    get_events_to_fetch.event_dates = events_2026_plus
    
    return unfetched, fetcher, existing_hands
    
    # Return events not yet fetched, sorted, plus the existing hands set
    unfetched = [e for e in events_2026_plus if str(e) not in fetched_events]
    return sorted(unfetched), fetcher, existing_hands

def main():
    events, fetcher, existing_hands = get_events_to_fetch()
    
    # Get the event dates we collected during get_events_to_fetch()
    event_dates = getattr(get_events_to_fetch, 'event_dates', {})
    
    initial_count = len(fetcher.hands)
    print(f"Fetching hands from {len(events)} events in 2026 onwards...")
    print(f"Starting with: {initial_count} hands (will skip duplicates)\n")
    
    total_added = 0
    total_skipped = 0
    total_ignored = 0  # Pre-2026 hands
    
    if len(events) == 0:
        print("✅ All events already fetched! No new data to retrieve.\n")
    
    for idx, event_id in enumerate(events, 1):
        try:
            start = time.time()
            
            # Fetch hands for this event
            hands = fetcher.fetch_hands_for_event(event_id)
            elapsed = time.time() - start
            
            # Get the date for this event from our collected data
            event_date = event_dates.get(event_id)
            
            # Process hands: add only new 2026+ hands
            new_count = 0
            skipped_count = 0
            ignored_count = 0
            
            for hand in hands:
                # Set the date from our known event dates
                if event_date and (not hand.get('date') or hand.get('date') == 'unknown'):
                    hand['date'] = event_date
                
                # Filter 1: Only keep hands from 2026 or later
                if not is_hand_from_2026_or_later(hand):
                    ignored_count += 1
                    continue
                
                # Filter 2: Skip if already in database
                event_board = (hand.get('event_id'), hand.get('board'))
                if event_board in existing_hands:
                    skipped_count += 1
                    continue
                
                # Add new hand
                fetcher.hands.append(hand)
                existing_hands.add(event_board)
                new_count += 1
            
            total_added += new_count
            total_skipped += skipped_count
            total_ignored += ignored_count
            
            status = f"✓ fetched {len(hands)} hands"
            details = []
            if new_count > 0:
                details.append(f"+{new_count} new")
            if skipped_count > 0:
                details.append(f"-{skipped_count} skipped")
            if ignored_count > 0:
                details.append(f"-{ignored_count} pre-2026")
            
            if details:
                status += f" ({', '.join(details)})"
            
            print(f"[{idx:3d}/{len(events)}] Event {event_id}: {status} ({elapsed:.1f}s)")
            
            # Save after each event to preserve progress
            with open('hands_database.json', 'w', encoding='utf-8') as f:
                json.dump(fetcher.hands, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"[{idx:3d}/{len(events)}] Event {event_id}: ✗ Error: {e}")
            continue
    
    final_count = len(fetcher.hands)
    print(f"\n{'='*60}")
    print(f"✅ Fetch Complete!")
    print(f"Initial hands: {initial_count}")
    print(f"Hands added: {total_added}")
    print(f"Hands skipped (duplicates): {total_skipped}")
    print(f"Hands ignored (pre-2026): {total_ignored}")
    print(f"Final hands: {final_count}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
