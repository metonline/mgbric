#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fetch all hands from Vugraph (1.1.2026 - now), calculate DD, organize by tournament
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import sys
import os
from urllib.parse import quote

class RecentHandsFetcher:
    """Fetch recent tournament hands from Vugraph"""
    
    BASE_URL = "https://clubs.vugraph.com/hosgoru"
    
    def __init__(self):
        self.tournaments = {}
        self.hands_by_tournament = {}
        self.start_date = datetime(2026, 1, 1)
        self.end_date = datetime.now()
    
    def get_calendar_dates(self):
        """Get list of dates from start to now"""
        current = self.start_date
        dates = []
        while current <= self.end_date:
            dates.append(current.strftime("%d.%m.%Y"))
            current += timedelta(days=1)
        return dates
    
    def fetch_tournaments_for_date(self, date_str):
        """
        Fetch tournaments for a specific date from calendar
        date_str format: "1.1.2026"
        """
        try:
            response = requests.get(f"{self.BASE_URL}/calendar.php", timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            tournaments = []
            
            # Parse calendar table for events on this date
            # Look for links with tournament data
            for link in soup.find_all('a'):
                href = link.get('href', '')
                if 'eventnum=' in href:
                    text = link.get_text(strip=True)
                    # Extract event number
                    if 'eventnum=' in href:
                        event_id = href.split('eventnum=')[1].split('&')[0]
                        tournaments.append({
                            'id': event_id,
                            'name': text,
                            'date': date_str,
                            'url': href
                        })
            
            return tournaments
        except Exception as e:
            print(f"Error fetching tournaments for {date_str}: {e}")
            return []
    
    def fetch_tournament_hands(self, event_id):
        """Fetch all hands for a tournament"""
        try:
            url = f"{self.BASE_URL}/viewhand.php?eventnum={event_id}"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            hands = []
            
            # Parse hands from the page
            # Look for board links
            for link in soup.find_all('a'):
                href = link.get('href', '')
                if 'boardnum=' in href and 'eventnum=' in href:
                    board_num = href.split('boardnum=')[1].split('&')[0]
                    text = link.get_text(strip=True)
                    
                    hands.append({
                        'board': board_num,
                        'event_id': event_id,
                        'url': href
                    })
            
            return hands
        except Exception as e:
            print(f"Error fetching hands for event {event_id}: {e}")
            return []
    
    def fetch_hand_details(self, event_id, board_num):
        """Fetch detailed hand information"""
        try:
            url = f"{self.BASE_URL}/viewhand.php?eventnum={event_id}&boardnum={board_num}"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract deal, dealer, vulnerability
            hand_data = {
                'event_id': event_id,
                'board': board_num,
                'deal': None,
                'dealer': None,
                'vulnerability': None,
                'html': response.text
            }
            
            # Parse the page to extract hand information
            # Look for deal display or PBN format
            text = soup.get_text()
            
            # Extract dealer (usually shown as "Dealer: N" or similar)
            if 'Dealer:' in text or 'dealer:' in text:
                for part in text.split():
                    if part in ['N', 'E', 'S', 'W']:
                        hand_data['dealer'] = part
                        break
            
            # Extract vulnerability
            vuln_map = {
                'None': 'None',
                'NS': 'NS', 
                'E-W': 'EW',
                'All': 'Both'
            }
            for key, val in vuln_map.items():
                if key in text:
                    hand_data['vulnerability'] = val
                    break
            
            return hand_data
        except Exception as e:
            print(f"Error fetching hand details {event_id}/{board_num}: {e}")
            return None
    
    def fetch_all_recent(self):
        """Main function to fetch all recent tournaments and hands"""
        print(f"Fetching tournaments from {self.start_date.date()} to {self.end_date.date()}...")
        
        dates = self.get_calendar_dates()
        print(f"Will check {len(dates)} dates")
        
        all_tournaments = {}
        
        for date_str in dates[-7:]:  # Check last 7 days for now
            print(f"Fetching tournaments for {date_str}...")
            tournaments = self.fetch_tournaments_for_date(date_str)
            
            for tourney in tournaments:
                if tourney['id'] not in all_tournaments:
                    all_tournaments[tourney['id']] = tourney
                    print(f"  Found: {tourney['name']} (ID: {tourney['id']})")
        
        print(f"\nTotal tournaments found: {len(all_tournaments)}")
        
        # Fetch hands for each tournament
        hands_by_tournament = {}
        for event_id, tournament in all_tournaments.items():
            print(f"Fetching hands for {tournament['name']}...")
            hands = self.fetch_tournament_hands(event_id)
            if hands:
                hands_by_tournament[event_id] = {
                    'tournament': tournament,
                    'hands': hands
                }
                print(f"  Found {len(hands)} boards")
        
        return hands_by_tournament

def main():
    fetcher = RecentHandsFetcher()
    
    print("=" * 60)
    print("FETCHING RECENT HANDS FROM VUGRAPH")
    print("=" * 60)
    
    hands_data = fetcher.fetch_all_recent()
    
    # Save to JSON for processing
    output_file = 'recent_tournaments_raw.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(hands_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nRaw data saved to {output_file}")
    print(f"Tournaments: {len(hands_data)}")
    total_hands = sum(len(t['hands']) for t in hands_data.values())
    print(f"Total hands: {total_hands}")

if __name__ == '__main__':
    main()
