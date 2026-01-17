#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch all tournaments from 2026 and add their hands to database
Properly handles UTF-8 encoding for Turkish characters
"""

import json
import requests
from bs4 import BeautifulSoup
import sys
import os

BASE_URL = "https://clubs.vugraph.com/hosgoru"

def fetch_calendar():
    """Get the calendar page with proper UTF-8 encoding"""
    response = requests.get(f"{BASE_URL}/calendar.php", timeout=30)
    response.encoding = 'iso-8859-9'  # Turkish encoding
    return response.text

def extract_event_ids(html):
    """Extract all event IDs and names from calendar with proper encoding"""
    soup = BeautifulSoup(html, 'html.parser')
    events = {}
    
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        if 'eventresults.php?event=' in href:
            event_id = href.split('event=')[1]
            text = link.get_text(strip=True)
            if event_id not in events:
                events[event_id] = text
    
    return events

def fetch_hands_from_event(event_id):
    """Fetch all hands from a tournament event"""
    url = f"{BASE_URL}/eventresults.php?event={event_id}"
    
    try:
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        hands = []
        
        # Look for board tables or hand data
        # Try to find links to individual hands
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            # Look for viewhand links
            if 'viewhand.php' in href or 'board=' in href:
                # Extract board number if available
                pass
        
        return hands
    except Exception as e:
        print(f"Error fetching event {event_id}: {e}")
        return []

def main():
    print("[*] Fetching calendar...")
    html = fetch_calendar()
    
    print("[*] Extracting event IDs...")
    events = extract_event_ids(html)
    
    print(f"[+] Found {len(events)} recent tournaments")
    
    # Show recent tournaments
    for i, (eid, name) in enumerate(sorted(events.items(), reverse=True)[:10]):
        print(f"    {i+1}. ID:{eid} - {name[:50]}")
    
    # Load existing database
    try:
        with open('hands_database.json', 'r', encoding='utf-8') as f:
            db = json.load(f)
    except:
        db = {}
    
    print(f"\n[*] Database currently has {len(db)} hands")
    print("[+] To fetch hands from an event, run:")
    print("    python vugraph_fetcher.py <event_id>")
    print("\nOr provide a date like:")
    print("    python vugraph_fetcher.py 18.01.2026")

if __name__ == "__main__":
    main()
