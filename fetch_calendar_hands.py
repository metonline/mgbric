#!/usr/bin/env python3
"""
Fetch all hands from Hoşgörü vugraph for January 2026
Uses the calendar page to find all event IDs, then fetches hands from each
"""

import json
import requests
from bs4 import BeautifulSoup
import time
import re

# Keep existing hands
try:
    with open('hands_database.json', 'r') as f:
        existing_hands = json.load(f)
    existing_events = {h.get('event_id') for h in existing_hands}
    print(f"✅ Loaded {len(existing_hands)} existing hands from {len(existing_events)} events")
except:
    existing_hands = []
    existing_events = set()

all_hands = {h.get('event_id'): len([x for x in existing_hands if x.get('event_id') == h.get('event_id')]) 
             for h in existing_hands}

base_url = "https://clubs.vugraph.com/hosgoru"
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

print("📅 Fetching calendar...")
try:
    resp = session.get(f"{base_url}/calendar.php?month=1&year=2026", timeout=10)
    soup = BeautifulSoup(resp.content, 'html.parser')
    
    # Find all event links in the calendar
    event_links = soup.find_all('a', href=re.compile(r'eventresults\.php\?event=\d+'))
    
    event_ids = []
    for link in event_links:
        match = re.search(r'event=(\d+)', link.get('href', ''))
        if match:
            event_id = match.group(1)
            if event_id not in event_ids:
                event_ids.append(event_id)
    
    print(f"✅ Found {len(event_ids)} unique events in January 2026")
    print(f"\nEvent IDs: {', '.join(event_ids[:10])}...")
    
    # Now fetch hands from each event
    total_new_hands = 0
    
    for i, event_id in enumerate(event_ids, 1):
        print(f"\n[{i}/{len(event_ids)}] Fetching event {event_id}...")
        
        try:
            # Fetch event results page
            event_url = f"{base_url}/eventresults.php?event={event_id}"
            resp_event = session.get(event_url, timeout=10)
            
            if resp_event.status_code == 200:
                soup_event = BeautifulSoup(resp_event.content, 'html.parser')
                
                # Look for hand viewing links or hand data
                hand_links = soup_event.find_all('a', href=re.compile(r'hand|hands|board', re.I))
                
                if hand_links:
                    print(f"  ✓ Found {len(hand_links)} potential hand links")
                    # Try to fetch hands
                    for link in hand_links[:5]:  # Try first 5
                        href = link.get('href', '')
                        print(f"    - {href[:60]}")
                else:
                    print(f"  ⏭️  No hand links found")
            
            time.sleep(1)
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print(f"\n{'='*60}")
    print(f"📊 Results:")
    print(f"  Total events scanned: {len(event_ids)}")
    print(f"  Existing hands: {len(existing_hands)}")
    print(f"  New hands added: {total_new_hands}")

except Exception as e:
    print(f"❌ Error fetching calendar: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Calendar scan complete")
