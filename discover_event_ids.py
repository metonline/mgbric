#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct scraper to get event list from Vugraph events page
"""

import requests
from bs4 import BeautifulSoup
import re
import json

def fetch_event_ids_for_january():
    """Fetch event IDs for January 2026 from Vugraph"""
    
    print("=" * 70)
    print("🔍 Fetching Event IDs from Vugraph Calendar")
    print("=" * 70)
    
    events_by_date = {}
    
    # Try different URL patterns for Vugraph
    urls_to_try = [
        "https://clubs.vugraph.com/hosgoru/calendar.php",
        "https://clubs.vugraph.com/hosgoru/events.php?year=2026&month=1",
        "https://clubs.vugraph.com/hosgoru/turnuvalar.php",
    ]
    
    for url in urls_to_try:
        try:
            print(f"\n🌐 Trying: {url}")
            response = requests.get(url, timeout=10)
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all links that have event= parameter
            all_links = soup.find_all('a', href=True)
            
            event_found = False
            
            for link in all_links:
                href = link.get('href', '')
                text = link.get_text().strip()
                
                if 'event=' in href:
                    # Extract event ID
                    match = re.search(r'event=(\d+)', href)
                    if match:
                        event_id = match.group(1)
                        
                        # Try to find date in text or link title
                        # Common patterns: DD.MM.YYYY or DD Ay YYYY
                        date_pattern = r'(\d{1,2})\.(\d{1,2})\.(\d{4})'
                        date_match = re.search(date_pattern, text)
                        
                        if date_match:
                            day = date_match.group(1).zfill(2)
                            month = date_match.group(2).zfill(2)
                            year = date_match.group(3)
                            
                            # Only January 2026
                            if year == '2026' and month == '01':
                                date_key = f"{year}-{month}-{day}"
                                
                                if date_key not in events_by_date:
                                    events_by_date[date_key] = []
                                
                                events_by_date[date_key].append({
                                    'event_id': event_id,
                                    'name': text,
                                    'url': href
                                })
                                
                                event_found = True
            
            if event_found:
                print(f"   ✅ Found events in this page")
                break
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue
    
    if not events_by_date:
        print("\n⚠️  Could not find event IDs from Vugraph")
        print("\n💡 Known tournament:")
        print("   • 2026-01-04: Event 404377 (PAZAR SİMULTANE)")
        print("\n📝 Please check https://clubs.vugraph.com/hosgoru/calendar.php manually")
        print("   and note the event IDs for each date\n")
        
        return None
    
    # Display results
    print("\n" + "=" * 70)
    print("📋 Events found for January 2026:")
    print("=" * 70)
    
    for date_key in sorted(events_by_date.keys()):
        events = events_by_date[date_key]
        print(f"\n📅 {date_key}:")
        for event in events:
            print(f"   • Event {event['event_id']}: {event['name']}")
    
    return events_by_date

def manual_entry():
    """Ask user to manually enter event IDs"""
    
    print("\n" + "=" * 70)
    print("⌨️  Manual Event ID Entry")
    print("=" * 70)
    
    events = {}
    
    dates = [
        '2026-01-01',
        '2026-01-02',
        '2026-01-03',
        '2026-01-04',
        '2026-01-05',
        '2026-01-06',
        '2026-01-07'
    ]
    
    for date in dates:
        event_id_input = input(f"\nEvent ID for {date} (or press Enter to skip): ").strip()
        
        if event_id_input:
            if date not in events:
                events[date] = []
            
            events[date].append({
                'event_id': event_id_input,
                'name': f'Tournament {date}'
            })
    
    return events if events else None

def main():
    # Try to fetch from Vugraph
    events = fetch_event_ids_for_january()
    
    if not events:
        # Ask for manual entry
        response = input("\n❓ Try manual entry? (y/n): ").strip().lower()
        if response == 'y':
            events = manual_entry()
    
    if events:
        # Collect all event IDs
        all_event_ids = []
        
        for date, event_list in sorted(events.items()):
            for event in event_list:
                all_event_ids.append(event['event_id'])
        
        print("\n" + "=" * 70)
        print(f"✅ Event IDs to fetch: {', '.join(all_event_ids)}")
        print("=" * 70)
        
        print("\n📝 Next steps:")
        print("1. Run: python fetch_vugraph_hands.py")
        print("2. Enter event IDs when prompted")
        print(f"3. Suggested input: {', '.join(all_event_ids)}")

if __name__ == '__main__':
    main()
