#!/usr/bin/env python3
"""
Fetch all hands from all January 2026 events using pairsummary endpoint
"""

import json
import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime

# Keep existing hands
try:
    with open('hands_database.json', 'r') as f:
        existing_hands = json.load(f)
    existing_ids = {f"{h.get('event_id')}_{h.get('board')}" for h in existing_hands}
    print(f"✅ Loaded {len(existing_hands)} existing hands")
except:
    existing_hands = []
    existing_ids = set()

all_hands = existing_hands.copy()

base_url = "https://clubs.vugraph.com/hosgoru"
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0'})

# Events from January 2026 calendar
events = [
    ('404155', '01.01.2026'),
    ('404197', '02.01.2026'),
    ('404275', '03.01.2026'),
    ('404377', '04.01.2026'),
    ('404426', '05.01.2026'),
    ('404498', '06.01.2026'),
    ('404562', '07.01.2026'),
    ('404628', '08.01.2026'),
    ('404691', '09.01.2026'),
    ('404854', '10.01.2026'),
    ('404821', '11.01.2026'),
    ('404876', '12.01.2026'),
    ('405128', '13.01.2026'),
    ('405007', '14.01.2026'),
    ('405061', '15.01.2026'),
    ('405123', '16.01.2026'),
    ('405204', '17.01.2026'),
    ('405278', '18.01.2026'),
    ('405315', '19.01.2026'),
    ('405376', '20.01.2026'),
    ('405445', '21.01.2026'),
    ('405535', '22.01.2026'),
    ('405596', '23.01.2026'),
]

print(f"📚 Will fetch from {len(events)} events\n")

total_new_hands = 0

for event_id, event_date in events:
    print(f"[{events.index((event_id, event_date))+1}/{len(events)}] Event {event_id} ({event_date})...")
    
    try:
        hands_in_event = 0
        
        # Try different sections and pairs
        for section in ['A', 'B', 'C']:  # Common sections
            for pair in range(1, 20):  # Try up to 19 pairs per section
                for direction in ['NS', 'EW']:
                    try:
                        # Build pairsummary URL
                        pair_url = f"{base_url}/pairsummary.php?event={event_id}&section={section}&pair={pair}&direction={direction}"
                        
                        resp = session.get(pair_url, timeout=5)
                        
                        if resp.status_code == 200:
                            soup = BeautifulSoup(resp.content, 'html.parser')
                            
                            # Look for hand data in the page
                            # Parse tables or any hand-like structure
                            text = soup.get_text()
                            
                            # Look for board numbers and hand data
                            if 'Board' in text or 'board' in text or any(suit in text for suit in ['♠', '♥', '♦', '♣']):
                                # Try to extract hands
                                tables = soup.find_all('table')
                                
                                for table in tables:
                                    rows = table.find_all('tr')
                                    for row in rows:
                                        cells = row.find_all(['td', 'th'])
                                        if len(cells) >= 4:
                                            row_text = ' '.join([c.get_text() for c in cells])
                                            
                                            # Check for hand pattern
                                            if any(suit in row_text for suit in ['♠', '♥', '♦', '♣', '.K', '.Q', '.A']):
                                                # Extract hand data
                                                hand_match = re.search(r'([AKQJT98765432]+)\.([AKQJT98765432]+)\.([AKQJT98765432]+)\.([AKQJT98765432]+)', row_text)
                                                if hand_match:
                                                    hands_in_event += 1
                        
                        time.sleep(0.2)  # Be polite
                        
                    except:
                        pass
        
        if hands_in_event > 0:
            print(f"  ✓ Found {hands_in_event} hands")
            total_new_hands += hands_in_event
        else:
            print(f"  ⏭️  No hands found")
    
    except Exception as e:
        print(f"  ❌ Error: {e}")

print(f"\n{'='*60}")
print(f"✅ Crawl complete")
print(f"📊 Total new hands found: {total_new_hands}")
print(f"📚 Total hands in database: {len(all_hands)}")
