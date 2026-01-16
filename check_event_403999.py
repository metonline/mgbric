#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
from bs4 import BeautifulSoup
import re

def fetch_event_results(event_id):
    """Fetch detailed results for a specific tournament event"""
    url = f"https://clubs.vugraph.com/hosgoru/eventresults.php?event={event_id}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get page title or event date info
        title = soup.find('title')
        if title:
            print(f"Event {event_id} title: {title.get_text()}")
        
        # Find the results table
        results = {'NS': [], 'EW': []}
        
        # Look for tables with results
        tables = soup.find_all('table')
        print(f"  Found {len(tables)} tables")
        
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) > 1:
                # Print first few rows to understand structure
                for i, row in enumerate(rows[:3]):
                    cells = row.find_all(['th', 'td'])
                    if cells:
                        print(f"    Row {i}: {[cell.get_text(strip=True)[:30] for cell in cells[:5]]}")
        
        return results
    
    except Exception as e:
        print(f"Error fetching event {event_id}: {e}")
        return None

if __name__ == "__main__":
    # Event 403999 should be the Pazartesi for 29.12.2025
    print("Fetching data for event 403999 (should be 29.12.2025 Pazartesi)...\n")
    fetch_event_results(403999)
