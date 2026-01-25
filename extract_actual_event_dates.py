#!/usr/bin/env python3
"""
Extract actual event dates from vugraph event detail pages and update database
"""

import json
import requests
from bs4 import BeautifulSoup
from collections import defaultdict

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def extract_event_date(event_id):
    """Extract the actual date from event's detail page"""
    try:
        url = f"https://clubs.vugraph.com/hosgoru/eventdetails.php?event={event_id}"
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for date in the page - usually in a table or header
        # Common patterns: "Tarih:", "Date:", "Tournament Date"
        text = soup.get_text()
        
        # Try to find date pattern DD.MM.YYYY
        import re
        dates = re.findall(r'\d{1,2}\.\d{1,2}\.\d{4}', text)
        
        if dates:
            # Usually the first date is the event date
            return dates[0]
        
        # Fallback: look in title or specific tags
        title = soup.find('title')
        if title:
            title_text = title.get_text()
            dates = re.findall(r'\d{1,2}\.\d{1,2}\.\d{4}', title_text)
            if dates:
                return dates[0]
        
        return None
    except Exception as e:
        print(f"  Error fetching event {event_id}: {e}")
        return None

def main():
    # Load database
    with open('hands_database.json', 'r', encoding='utf-8') as f:
        hands = json.load(f)
    
    print("="*70)
    print("Extracting actual event dates from vugraph event detail pages")
    print("="*70)
    
    # Group hands by event
    hands_by_event = defaultdict(list)
    for hand in hands:
        event_id = hand.get('event_id')
        if event_id:
            hands_by_event[event_id].append(hand)
    
    # Collect event IDs and their current placeholder dates
    events_to_update = {}
    for event_id in sorted(hands_by_event.keys()):
        current_date = hands_by_event[event_id][0].get('date', 'unknown')
        events_to_update[event_id] = current_date
    
    print(f"\nFound {len(events_to_update)} events with {len(hands)} hands total")
    print("\nFetching actual dates from event detail pages...")
    
    # Fetch actual dates
    actual_dates = {}
    for idx, event_id in enumerate(sorted(events_to_update.keys()), 1):
        current_date = events_to_update[event_id]
        actual_date = extract_event_date(event_id)
        
        if actual_date:
            status = f"✓ {actual_date}"
            if actual_date != current_date:
                status += f" (was: {current_date})"
            actual_dates[event_id] = actual_date
            print(f"[{idx:2d}/{len(events_to_update)}] Event {event_id}: {status}")
        else:
            status = f"✗ Could not extract (keeping: {current_date})"
            actual_dates[event_id] = current_date
            print(f"[{idx:2d}/{len(events_to_update)}] Event {event_id}: {status}")
    
    # Update database with actual dates
    print("\nUpdating database with actual dates...")
    updated_count = 0
    for hand in hands:
        event_id = hand.get('event_id')
        if event_id in actual_dates:
            old_date = hand.get('date')
            new_date = actual_dates[event_id]
            if old_date != new_date:
                hand['date'] = new_date
                updated_count += 1
    
    # Save updated database
    with open('hands_database.json', 'w', encoding='utf-8') as f:
        json.dump(hands, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Updated {updated_count} hands with actual dates")
    
    # Show summary
    print("\n" + "="*70)
    print("Date Distribution:")
    dates_summary = defaultdict(int)
    for hand in hands:
        dates_summary[hand.get('date')] += 1
    
    for date in sorted(dates_summary.keys()):
        print(f"  {date}: {dates_summary[date]} hands")
    
    print("="*70)

if __name__ == '__main__':
    main()
