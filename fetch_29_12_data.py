#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Vugraph calendar URL
CALENDAR_URL = "https://clubs.vugraph.com/hosgoru/calendar.php"

def fetch_tournaments_for_date(target_date_str):
    """
    Fetch tournaments for a specific date from Vugraph
    target_date_str format: "29.12.2025"
    """
    try:
        # Fetch calendar
        response = requests.get(CALENDAR_URL, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for the date in the calendar
        tournaments = []
        
        # Find all tournament links
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)
            
            # Check if this is an event result link
            if 'eventresults.php?event=' in href:
                print(f"Found tournament event: {text} - {href}")
                tournaments.append({
                    'name': text,
                    'url': href
                })
        
        return tournaments
    
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def fetch_event_results(event_url):
    """Fetch results for a specific tournament event"""
    try:
        response = requests.get(event_url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract tournament info and results
        results = {
            'NS': [],
            'EW': []
        }
        
        # Parse the results table
        # This needs to be customized based on Vugraph's HTML structure
        
        return results
    
    except Exception as e:
        print(f"Error fetching event: {e}")
        return None

if __name__ == "__main__":
    print("Fetching tournaments for 29.12.2025 from Vugraph...")
    tournaments = fetch_tournaments_for_date("29.12.2025")
    
    print(f"\nFound {len(tournaments)} tournaments")
    for i, t in enumerate(tournaments, 1):
        print(f"{i}. {t['name']}")
        print(f"   URL: {t['url']}")
