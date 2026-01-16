#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch tournament names from Vugraph event pages
Maps event IDs to tournament names and dates
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

EVENTS = [
    (404155, '2026-01-01'),
    (404197, '2026-01-02'),
    (404275, '2026-01-03'),
    (404377, '2026-01-04'),
    (404426, '2026-01-05'),
    (404498, '2026-01-06'),
]

def get_tournament_name(event_id):
    """Fetch tournament name and details from event page"""
    
    print(f"   Fetching Event {event_id}...", end='')
    
    try:
        url = f"https://clubs.vugraph.com/hosgoru/eventresults.php?event={event_id}"
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()
        
        # Extract any title or heading
        title = soup.title
        if title:
            title_text = title.get_text().strip()
            # Try to extract tournament name (usually between |  or -)
            parts = title_text.split('|')
            if len(parts) > 1:
                name = parts[-1].strip()
            else:
                name = title_text
        else:
            # Look for h1 or h2
            h1 = soup.find('h1')
            if h1:
                name = h1.get_text().strip()
            else:
                h2 = soup.find('h2')
                if h2:
                    name = h2.get_text().strip()
                else:
                    name = f"Tournament {event_id}"
        
        print(f" ✓")
        return name
    
    except Exception as e:
        print(f" ✗ ({e})")
        return f"Tournament {event_id}"

def main():
    print("=" * 70)
    print("📋 Tournament Name Fetcher")
    print("=" * 70)
    print()
    
    event_mapping = {}
    
    for event_id, date in EVENTS:
        name = get_tournament_name(event_id)
        event_mapping[event_id] = {
            'date': date,
            'name': name
        }
    
    # Display results
    print(f"\n{'=' * 70}")
    print("📊 Tournament Mapping:")
    print(f"{'=' * 70}")
    
    for event_id, date in EVENTS:
        info = event_mapping[event_id]
        print(f"\nEvent {event_id} ({info['date']}):")
        print(f"  Name: {info['name']}")
    
    # Save for reference
    with open('event_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(event_mapping, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Mapping saved to event_mapping.json")

if __name__ == '__main__':
    main()
