#!/usr/bin/env python3
"""
Fetch hands from all events using pairsummary.php endpoint
"""

import json
import requests
from bs4 import BeautifulSoup
import re
import time

# Keep existing hands
try:
    with open('hands_database.json', 'r') as f:
        existing_hands = json.load(f)
    existing_event_ids = {h.get('event_id') for h in existing_hands}
    print(f"✅ Loaded {len(existing_hands)} existing hands")
except:
    existing_hands = []
    existing_event_ids = set()

all_hands = existing_hands.copy()

base_url = "https://clubs.vugraph.com/hosgoru"
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

# List of all events in January 2026
events = ['404155', '404197', '404275', '404377', '404426', '404498', '404562', 
          '404628', '404691', '404854', '404821', '404876', '405128', '405007', 
          '405061', '405123', '405204', '405278', '405315', '405376', '405445', 
          '405535', '405596']

print(f"📊 {len(events)} events to process\n")

new_hands_count = 0

for event_id in events:
    print(f"📌 Event {event_id}...", end=" ")
    
    try:
        # Try to fetch pairsummary for first pair and section
        # Typical structure: pairs 1-n, sections might be A/B etc
        
        hands_found_in_event = 0
        
        for pair in range(1, 50):  # Try pairs 1-50
            for section in ['A', 'B', 'C']:
                for direction in ['NS', 'EW']:
                    try:
                        pair_url = f"{base_url}/pairsummary.php?event={event_id}&section={section}&pair={pair}&direction={direction}"
                        resp = session.get(pair_url, timeout=5)
                        
                        if resp.status_code == 200 and len(resp.text) > 500:
                            # Parse for hand data
                            soup = BeautifulSoup(resp.content, 'html.parser')
                            
                            # Look for board/hand tables
                            tables = soup.find_all('table')
                            for table in tables:
                                rows = table.find_all('tr')
                                for row in rows:
                                    cells = row.find_all(['td', 'th'])
                                    row_text = ' '.join([c.get_text() for c in cells])
                                    
                                    # Look for hand data pattern
                                    if any(suit in row_text for suit in ['♠', '♥', '♦', '♣']):
                                        hands_found_in_event += 1
                        
                        time.sleep(0.2)  # Be polite
                    except:
                        pass
                
                if hands_found_in_event > 100:  # If we found a lot, stop
                    break
            
            if hands_found_in_event > 100:
                break
        
        if hands_found_in_event > 0:
            print(f"✅ {hands_found_in_event} hands")
            new_hands_count += hands_found_in_event
        else:
            print(f"⏭️")
    
    except Exception as e:
        print(f"❌ {e}")

print(f"\n{'='*60}")
print(f"✅ Complete")
print(f"🃏 New hands found: {new_hands_count}")
