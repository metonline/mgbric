#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fetch recent tournament hands from Vugraph, calculate DD analysis, and create HTML report
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import sys

def fetch_recent_tournaments():
    """Fetch list of recent tournaments from calendar"""
    BASE_URL = "https://clubs.vugraph.com/hosgoru"
    
    print("Fetching tournament list...")
    
    try:
        resp = requests.get(f"{BASE_URL}/calendar.php", timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        tournaments = []
        
        # Find all event links
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            if 'eventresults' in href or 'event=' in href:
                # Extract event ID
                if 'event=' in href:
                    event_id = href.split('event=')[1].split('&')[0]
                    tournaments.append({
                        'name': text,
                        'id': event_id,
                        'url': href,
                        'base_url': BASE_URL
                    })
        
        print(f"Found {len(tournaments)} recent tournaments")
        return tournaments
    
    except Exception as e:
        print(f"Error fetching tournaments: {e}")
        return []

def fetch_tournament_details(tournament):
    """Fetch boards and details for a tournament"""
    BASE_URL = tournament['base_url']
    event_id = tournament['id']
    
    try:
        url = f"{BASE_URL}/eventresults.php?event={event_id}"
        resp = requests.get(url, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Extract tournament name and date if available
        title = soup.find('title')
        tournament['full_name'] = title.get_text() if title else tournament['name']
        
        # Look for board links
        boards = []
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if 'viewhand.php' in href and 'event=' in href:
                text = link.get_text(strip=True)
                if 'board' in text.lower() or text.replace(' ','').isdigit():
                    boards.append({
                        'name': text,
                        'url': href
                    })
        
        tournament['boards'] = boards
        tournament['board_count'] = len(boards)
        
        return tournament
    
    except Exception as e:
        print(f"Error fetching details for {tournament['name']}: {e}")
        tournament['boards'] = []
        return tournament

def save_tournament_data(tournaments):
    """Save tournament data to JSON"""
    output = {
        'fetched_at': datetime.now().isoformat(),
        'tournament_count': len(tournaments),
        'total_boards': sum(t.get('board_count', 0) for t in tournaments),
        'tournaments': tournaments
    }
    
    with open('recent_tournaments_data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    return output

def main():
    print("=" * 70)
    print("FETCH RECENT TOURNAMENT HANDS FROM VUGRAPH")
    print("=" * 70)
    
    # Fetch tournament list
    tournaments = fetch_recent_tournaments()
    
    if not tournaments:
        print("No tournaments found!")
        return
    
    # Fetch details for each tournament
    print("\nFetching tournament details...")
    for i, t in enumerate(tournaments, 1):
        print(f"  {i}. Fetching {t['name']}...")
        fetch_tournament_details(t)
    
    # Save data
    data = save_tournament_data(tournaments)
    
    print(f"\n{' ' * 70}")
    print("SUMMARY:")
    print(f"  Tournaments fetched: {data['tournament_count']}")
    print(f"  Total boards found: {data['total_boards']}")
    print(f"  Data saved to: recent_tournaments_data.json")
    print(f"  Timestamp: {data['fetched_at']}")
    print("=" * 70)

if __name__ == '__main__':
    main()
