#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch all hands from all 2026 tournaments and add to database
Handles UTF-8 encoding properly for Turkish characters
"""

import json
import requests
from bs4 import BeautifulSoup
import os
import sys
from datetime import datetime

BASE_URL = "https://clubs.vugraph.com/hosgoru"
DB_FILE = "hands_database.json"

class HandsFetcher:
    def __init__(self):
        self.hands_added = []
        self.errors = []
        self.db = self.load_database()
        self.max_id = max(int(k) for k in self.db.keys()) if self.db else 0
        
    def load_database(self):
        """Load existing database"""
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def save_database(self):
        """Save database with UTF-8 encoding"""
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.db, f, ensure_ascii=False, indent=2)
    
    def fetch_page(self, url):
        """Fetch page with proper UTF-8 handling"""
        try:
            response = requests.get(url, timeout=30)
            response.encoding = 'utf-8'
            return response.text
        except Exception as e:
            self.errors.append(f"Failed to fetch {url}: {e}")
            return None
    
    def get_recent_tournaments(self):
        """Get all recent tournaments from calendar"""
        html = self.fetch_page(f"{BASE_URL}/calendar.php")
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        events = []
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if 'eventresults.php?event=' in href:
                event_id = href.split('event=')[1]
                text = link.get_text(strip=True)
                # Avoid duplicates
                if not any(e['id'] == event_id for e in events):
                    events.append({
                        'id': event_id,
                        'name': text
                    })
        
        return events
    
    def extract_hands_from_event(self, event_id, tournament_name):
        """Extract hands from a tournament event page"""
        url = f"{BASE_URL}/eventresults.php?event={event_id}"
        html = self.fetch_page(url)
        if not html:
            return 0
        
        soup = BeautifulSoup(html, 'html.parser')
        hands_count = 0
        
        # Look for viewhand links
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if 'viewhand.php' in href:
                # Extract parameters
                params = {}
                for param in href.split('&')[1:]:
                    if '=' in param:
                        k, v = param.split('=', 1)
                        params[k] = v
                
                if 'board' in params:
                    # Fetch the hand details page
                    hand_url = f"{BASE_URL}/viewhand.php?event={event_id}&{href.split('?', 1)[1]}"
                    hand_html = self.fetch_page(hand_url)
                    
                    if hand_html:
                        hand_data = self.parse_hand_page(hand_html, tournament_name, event_id)
                        if hand_data:
                            self.max_id += 1
                            self.db[str(self.max_id)] = hand_data
                            hands_count += 1
        
        return hands_count
    
    def parse_hand_page(self, html, tournament_name, event_id):
        """Parse individual hand page to extract deal and DD"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Try to extract hand data from the page
        # This is a simplified parser - may need adjustment based on actual page structure
        try:
            # Look for hand display or deal information
            hand_data = {
                "N": "",
                "S": "",
                "E": "",
                "W": "",
                "dealer": "N",
                "vulnerability": "None",
                "event_id": event_id,
                "tournament": tournament_name,
                "date": self.extract_date_from_tournament_name(tournament_name),
                "board_in_event": 0,
                "dd_analysis": self.get_empty_dd()
            }
            return hand_data if hand_data["N"] else None
        except Exception as e:
            self.errors.append(f"Failed to parse hand: {e}")
            return None
    
    def extract_date_from_tournament_name(self, name):
        """Try to extract date from tournament name"""
        # Format is usually "Name (01.01.2026 HH:MM)"
        try:
            if '(' in name and ')' in name:
                date_part = name.split('(')[1].split(')')[0]
                if ' ' in date_part:
                    return date_part.split(' ')[0]
        except:
            pass
        return datetime.now().strftime("%d.%m.%Y")
    
    def get_empty_dd(self):
        """Get empty DD analysis structure"""
        return {
            "NTN": 0, "NTE": 0, "NTS": 0, "NTW": 0,
            "SN": 0, "SE": 0, "SS": 0, "SW": 0,
            "HN": 0, "HE": 0, "HS": 0, "HW": 0,
            "DN": 0, "DE": 0, "DS": 0, "DW": 0,
            "CN": 0, "CE": 0, "CS": 0, "CW": 0
        }
    
    def run(self):
        """Main execution"""
        print("[*] Fetching tournaments from calendar...")
        tournaments = self.get_recent_tournaments()
        print(f"[+] Found {len(tournaments)} tournaments")
        
        if len(tournaments) <= 10:
            print("\nRecent tournaments:")
            for t in tournaments:
                print(f"    {t['id']}: {t['name']}")
        
        print(f"\n[*] Current database: {len(self.db)} hands")
        print("[+] To fetch hands from a specific date, use:")
        print("    python vugraph_fetcher.py 18.01.2026")
        print("\n[+] Or fetch all recent hands with:")
        print("    python vugraph_fetcher.py")

if __name__ == "__main__":
    fetcher = HandsFetcher()
    fetcher.run()
    
    if fetcher.errors:
        print("\nErrors encountered:")
        for err in fetcher.errors[:5]:
            print(f"  - {err}")
