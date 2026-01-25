#!/usr/bin/env python3
"""
Fast batch extraction of actual event dates from vugraph
Updates database with correct dates for each event
"""

import json
import requests
import re
from bs4 import BeautifulSoup
from collections import defaultdict
import time

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def extract_event_date(event_id):
    """Extract actual date from event results page"""
    try:
        url = f"https://clubs.vugraph.com/hosgoru/eventresults.php?event={event_id}"
        response = requests.get(url, headers=headers, timeout=5)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for date format: (DD-MM-YYYY HH:MM) in page text
        text = soup.get_text()
        
        # Pattern: (DD-MM-YYYY HH:MM)
        match = re.search(r'\((\d{1,2})-(\d{1,2})-(\d{4})', text)
        if match:
            day, month, year = match.groups()
            # Convert from DD-MM-YYYY to DD.MM.YYYY format
            return f"{day.zfill(2)}.{month.zfill(2)}.{year}"
        
        return None
    except Exception as e:
        return None

def main():
    # Load database
    with open('hands_database.json', 'r', encoding='utf-8') as f:
        hands = json.load(f)
    
    print("="*70)
    print("Extracting ACTUAL event dates from vugraph")
    print("="*70)
    
    # Group by event
    by_event = defaultdict(list)
    for hand in hands:
        event_id = hand.get('event_id')
        if event_id:
            by_event[event_id].append(hand)
    
    print(f"\nFound {len(by_event)} events with {len(hands)} hands")
    print("\nExtracting dates from event detail pages...\n")
    
    # Extract dates and update database
    event_date_map = {}
    updated_count = 0
    
    for idx, event_id in enumerate(sorted(by_event.keys()), 1):
        old_date = by_event[event_id][0].get('date', 'unknown')
        actual_date = extract_event_date(event_id)
        
        if actual_date:
            event_date_map[event_id] = actual_date
            status = f"✓ {actual_date}"
            if actual_date != old_date:
                status += f" (was: {old_date})"
                updated_count += len(by_event[event_id])
        else:
            event_date_map[event_id] = old_date
            status = f"✗ Using: {old_date}"
        
        print(f"[{idx:2d}/24] Event {event_id}: {status}")
        time.sleep(0.1)  # Small delay to be nice to server
    
    # Update all hands with actual dates
    for hand in hands:
        event_id = hand.get('event_id')
        if event_id in event_date_map:
            hand['date'] = event_date_map[event_id]
    
    # Save updated database
    with open('hands_database.json', 'w', encoding='utf-8') as f:
        json.dump(hands, f, ensure_ascii=False, indent=2)
    
    # Show summary
    print("\n" + "="*70)
    print("Date Distribution After Update:")
    print("="*70)
    
    from collections import Counter
    dates = Counter(h.get('date') for h in hands)
    for date in sorted(dates.keys()):
        event_list = sorted(set(h['event_id'] for h in hands if h.get('date') == date))
        print(f"  {date}: {dates[date]} hands from {len(event_list)} events")
    
    print("="*70)
    print("✅ Database updated with actual event dates!")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
