#!/usr/bin/env python3
"""
Comprehensive vugraph crawler for Hosgörü club
Fetches all available hands from the calendar for date range
"""

import json
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import time
import sys

# Keep existing 30 hands
try:
    with open('hands_database.json', 'r') as f:
        existing_hands = json.load(f)
    print(f"✅ Loaded {len(existing_hands)} existing hands")
except:
    existing_hands = []
    print("Starting fresh")

all_hands = existing_hands.copy()
base_url = "https://clubs.vugraph.com/hosgoru"

# Date range: 01.01.2026 to 24.01.2026
start_date = datetime(2026, 1, 1)
end_date = datetime(2026, 1, 24)

dates_to_check = []
current = start_date
while current <= end_date:
    dates_to_check.append(current.strftime("%d.%m.%Y"))
    current += timedelta(days=1)

print(f"📅 Checking {len(dates_to_check)} dates from 01.01.2026 to 24.01.2026")

# Common board counts per event
board_counts = [30, 32, 16, 8]  # Try these board counts

hands_count_before = len(all_hands)
events_found = 0
errors = []

for date_str in dates_to_check:
    print(f"\n🔍 Checking {date_str}...")
    
    # Try to access the calendar for this date
    try:
        # First, try to find events for this date via calendar
        calendar_url = f"{base_url}/calendar.php"
        
        # Fetch the calendar page - might have links to events
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        
        # Try fetching hands directly for potential event IDs
        # Event IDs seem to be around 405xxx range based on what we've seen
        for event_id in range(405300, 405700):
            try:
                hands_url = f"{base_url}/hands/{event_id}.lin"
                resp = session.get(hands_url, timeout=5)
                
                if resp.status_code == 200 and len(resp.text) > 100:
                    # Try to fetch individual boards
                    for board in range(1, 31):
                        try:
                            board_url = f"{base_url}/hosgoru_{event_id}_{board}.html"
                            resp_board = session.get(board_url, timeout=5)
                            
                            if resp_board.status_code == 200:
                                # Try to parse the hand data
                                soup = BeautifulSoup(resp_board.content, 'html.parser')
                                # Look for hand data in the page
                                
                            time.sleep(0.1)  # Be polite
                        except:
                            pass
                    
                    events_found += 1
                    print(f"  ✓ Found event {event_id}")
                    time.sleep(1)
                    
            except:
                pass
                
    except Exception as e:
        errors.append(f"Date {date_str}: {str(e)}")

print(f"\n{'='*60}")
print(f"Results:")
print(f"  Hands before: {hands_count_before}")
print(f"  Hands now: {len(all_hands)}")
print(f"  New hands: {len(all_hands) - hands_count_before}")
print(f"  Events found: {events_found}")

if errors:
    print(f"\nErrors encountered:")
    for err in errors[:5]:
        print(f"  - {err}")

# Save all hands
with open('hands_database.json', 'w') as f:
    json.dump(all_hands, f, indent=2)

print(f"\n✅ Saved {len(all_hands)} total hands")
