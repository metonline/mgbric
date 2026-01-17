#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-fetch all hands from all 2026 tournaments
"""

import json
import requests
from bs4 import BeautifulSoup
import subprocess
import sys
from datetime import datetime

BASE_URL = "https://clubs.vugraph.com/hosgoru"

def get_recent_tournaments():
    """Get all recent tournaments"""
    response = requests.get(f"{BASE_URL}/calendar.php", timeout=30)
    response.encoding = 'iso-8859-9'
    
    soup = BeautifulSoup(response.text, 'html.parser')
    events = {}
    
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        if 'eventresults.php?event=' in href:
            event_id = href.split('event=')[1].split('&')[0]
            text = link.get_text(strip=True)
            # Extract date if available in text
            date = "18.01.2026"  # Default to today
            if '(' in text and ')' in text:
                try:
                    date_part = text.split('(')[1].split(')')[0]
                    if ' ' in date_part:
                        date = date_part.split(' ')[0]
                except:
                    pass
            
            if event_id not in events:
                events[event_id] = {'name': text, 'date': date}
    
    return events

def fetch_from_date(date_str):
    """Fetch hands from a specific date using vugraph_fetcher"""
    print(f"[*] Fetching from {date_str}...")
    try:
        result = subprocess.run([sys.executable, 'vugraph_fetcher.py', date_str], 
                              capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            # Count added records from output
            output = result.stdout
            if 'Added' in output:
                print(f"[+] {date_str}: Success")
                return True
            else:
                print(f"[-] {date_str}: No data")
                return False
        else:
            print(f"[-] {date_str}: Error")
            return False
    except subprocess.TimeoutExpired:
        print(f"[-] {date_str}: Timeout")
        return False
    except Exception as e:
        print(f"[-] {date_str}: {e}")
        return False

def main():
    print("[*] Getting recent tournaments...")
    tournaments = get_recent_tournaments()
    
    print(f"[+] Found {len(tournaments)} tournaments")
    
    # Group by date
    dates = {}
    for eid, info in tournaments.items():
        date = info['date']
        if date not in dates:
            dates[date] = []
        dates[date].append((eid, info['name']))
    
    print(f"\n[+] Found {len(dates)} unique dates:")
    for date in sorted(dates.keys(), reverse=True):
        print(f"    {date}: {len(dates[date])} tournaments")
    
    # Fetch from recent dates
    print("\n[*] Starting to fetch hands from recent tournaments...")
    print("[+] This may take a few minutes...\n")
    
    success_count = 0
    for date in sorted(dates.keys(), reverse=True)[:7]:  # Last 7 days
        if fetch_from_date(date):
            success_count += 1
    
    # Load and display results
    try:
        with open('hands_database.json', 'r', encoding='utf-8') as f:
            db = json.load(f)
        print(f"\n[+] Database now has {len(db)} hands")
    except:
        print("\n[-] Could not read database")

if __name__ == "__main__":
    main()
