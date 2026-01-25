#!/usr/bin/env python3
"""Restore missing dates for events from vugraph calendar"""
import json
import requests
from bs4 import BeautifulSoup
import re

def fetch_calendar_dates(month=1, year=2026):
    """Fetch event dates from vugraph calendar"""
    events = {}
    try:
        url = f"https://clubs.vugraph.com/hosgoru/calendar.php?month={month}&year={year}"
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all cells that might contain dates and event links
        for row in soup.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) >= 7:  # Week row
                for day_idx, cell in enumerate(cells):
                    # Look for event links in this cell
                    links = cell.find_all('a', href=True)
                    day = day_idx + 1
                    for link in links:
                        event_match = re.search(r'event=(\d+)', link['href'])
                        if event_match:
                            event_id = event_match.group(1)
                            date_str = f"{day:02d}.{month:02d}.{year}"
                            events[int(event_id)] = date_str
                            print(f"  Event {event_id}: {date_str}")
    except Exception as e:
        print(f"Error fetching calendar: {e}")
    
    return events

print("Fetching event dates from vugraph calendar...")
calendar_events = fetch_calendar_dates(1, 2026)
print(f"\nFound {len(calendar_events)} events with dates from calendar")

# Load database
with open('hands_database.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

# Update hands with dates from calendar
updated_count = 0
for hand in db:
    event_id = hand['event_id']
    if hand.get('date') == 'unknown' and event_id in calendar_events:
        hand['date'] = calendar_events[event_id]
        updated_count += 1

# Save updated database
with open('hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print(f"\n✓ Updated {updated_count} hands with dates from calendar")

# Verify
with open('hands_database.json', 'r', encoding='utf-8') as f:
    db_verify = json.load(f)
    unknown_hands = [h for h in db_verify if h.get('date') == 'unknown']
    print(f"\nRemaining hands with unknown date: {len(unknown_hands)}")
    
    dates = sorted({h.get('date') for h in db_verify})
    print(f"Updated dates in database: {sorted(dates)}")
    
    # Show summary by date
    for date in sorted(dates):
        hands_for_date = [h for h in db_verify if h.get('date') == date]
        print(f"  {date}: {len(hands_for_date)} hands")
