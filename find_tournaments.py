#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Find available Vugraph tournaments by date and fetch hands
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta

def find_tournaments_by_date(date_str):
    """Search Vugraph for tournaments on a specific date"""
    print(f"\n  Searching for tournaments on {date_str}...")
    
    # Vugraph uses a tournament list page
    # Try to access tournament archives
    url = f"https://clubs.vugraph.com/hosgoru/turnuvalar.php?date={date_str}"
    
    tournaments = []
    
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for tournament links/entries
        # Format varies - look for event IDs
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link['href']
            # Look for event= parameter
            if 'event=' in href:
                # Extract event ID
                import re
                match = re.search(r'event=(\d+)', href)
                if match:
                    event_id = match.group(1)
                    tournament_name = link.get_text().strip()
                    tournaments.append({
                        'event_id': int(event_id),
                        'name': tournament_name
                    })
        
        if tournaments:
            print(f"    Found {len(tournaments)} tournament(s):")
            for t in tournaments:
                print(f"    - Event {t['event_id']}: {t['name']}")
    
    except Exception as e:
        print(f"    Error searching for tournaments: {e}")
    
    return tournaments

def main():
    print("=" * 60)
    print("🔍 Vugraph Tournament Finder")
    print("=" * 60)
    
    start_date = datetime(2026, 1, 1)
    end_date = datetime.now()
    
    print(f"\nSearching tournaments from {start_date.date()} to {end_date.date()}...")
    
    all_tournaments = []
    current_date = start_date
    
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        tournaments = find_tournaments_by_date(date_str)
        all_tournaments.extend(tournaments)
        current_date += timedelta(days=1)
    
    # Remove duplicates
    unique_tournaments = {t['event_id']: t for t in all_tournaments}.values()
    
    if unique_tournaments:
        print(f"\n✅ Found {len(unique_tournaments)} unique tournament(s):")
        for t in sorted(unique_tournaments, key=lambda x: x['event_id']):
            print(f"   - Event {t['event_id']}: {t['name']}")
    else:
        print("\n⚠️  No tournaments found")
        print("   Known tournament from Vugraph:")
        print("   - Event 404377: PAZAR SİMULTANE 04-01-2026")

if __name__ == '__main__':
    main()
