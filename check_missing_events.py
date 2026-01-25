#!/usr/bin/env python3
"""Check which events exist for each day in January"""
import requests
from bs4 import BeautifulSoup
import re

def fetch_calendar_events_by_day(month=1, year=2026):
    """Fetch all events from calendar and group by day"""
    events_by_day = {}
    try:
        url = f"https://clubs.vugraph.com/hosgoru/calendar.php?month={month}&year={year}"
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the table
        table = soup.find('table')
        if not table:
            print("No calendar table found")
            return events_by_day
        
        rows = table.find_all('tr')
        
        # Skip header rows, start from first week
        for row_idx, row in enumerate(rows):
            cells = row.find_all('td')
            if len(cells) >= 7:  # Week row with 7 days
                for day_idx, cell in enumerate(cells):
                    day = day_idx + 1
                    
                    # Find all event links in this cell
                    links = cell.find_all('a', href=True)
                    events = []
                    for link in links:
                        event_match = re.search(r'event=(\d+)', link['href'])
                        if event_match:
                            event_id = int(event_match.group(1))
                            events.append(event_id)
                    
                    if events:
                        if day not in events_by_day:
                            events_by_day[day] = []
                        events_by_day[day].extend(events)
        
    except Exception as e:
        print(f"Error: {e}")
    
    return events_by_day

print("Fetching calendar events by day...")
events_by_day = fetch_calendar_events_by_day(1, 2026)

print("\nEvents by day in January 2026:")
for day in sorted(events_by_day.keys()):
    event_ids = sorted(set(events_by_day[day]))
    print(f"  Day {day:02d}: {len(event_ids)} events - {event_ids}")

# Check which days we have vs don't have
days_with_events = sorted(events_by_day.keys())
print(f"\nTotal days with events: {days_with_events}")

# Compare with what's in our database
import json
db = json.load(open('hands_database.json', encoding='utf-8'))
our_event_ids = {h['event_id'] for h in db}
our_dates = sorted({h.get('date') for h in db if h.get('date') and h.get('date') != 'unknown'})
our_days = sorted(set(int(d.split('.')[0]) for d in our_dates))

print(f"Days we have data for: {our_days}")
print(f"Event IDs we have: {sorted(our_event_ids)}")

missing_days = [d for d in days_with_events if d not in our_days]
print(f"\nMissing days: {missing_days}")

if missing_days:
    print("\nEvents on missing days:")
    for day in missing_days:
        event_ids = sorted(set(events_by_day[day]))
        print(f"  Day {day:02d}: {event_ids}")
        missing_events = [e for e in event_ids if e not in our_event_ids]
        if missing_events:
            print(f"    -> Missing event IDs: {missing_events}")
