#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup

CALENDAR_URL = "https://clubs.vugraph.com/hosgoru/calendar.php"

try:
    response = requests.get(CALENDAR_URL, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all tournament links
    all_links = soup.find_all('a', href=True)
    
    # Look for Pazartesi events (Monday)
    print("=== Pazartesi (Monday) Events ===\n")
    pazartesi_events = []
    
    for link in all_links:
        href = link['href']
        text = link.get_text(strip=True)
        
        if 'eventresults.php?event=' in href and 'Pazartesi' in text:
            event_num = href.split('event=')[1]
            pazartesi_events.append((event_num, text))
            print(f"Event {event_num}: {text}")
    
    print(f"\nTotal Pazartesi events found: {len(pazartesi_events)}")
    
    # Show the last few (most recent)
    print("\n=== Most Recent Pazartesi Events ===")
    for event_num, text in pazartesi_events[-3:]:
        print(f"  Event {event_num}: {text}")

except Exception as e:
    print(f"Error: {e}")
