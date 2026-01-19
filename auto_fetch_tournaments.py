#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Automatic Vugraph Tournament Data Fetcher
Fetches recent tournament data and updates the database automatically
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import sys
from vugraph_fetcher import VugraphDataFetcher

class AutoTournamentFetcher:
    """
    Automatically fetches tournament data for recent dates
    Can run on a schedule to keep database updated
    """
    
    def __init__(self):
        self.fetcher = VugraphDataFetcher()
        self.BASE_URL = "https://clubs.vugraph.com/hosgoru"
        
    def get_available_dates_from_calendar(self):
        """
        Extract all dates that have events from the calendar
        Returns list of dates with events - dynamically detects month/year
        """
        try:
            response = requests.get(f"{self.BASE_URL}/calendar.php", timeout=10)
            response.raise_for_status()
            html = response.text
        except Exception as e:
            print(f"Error fetching calendar: {e}")
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        dates_with_events = []
        
        # Try to detect current month/year from calendar header
        # Look for month/year in page title or header
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # Try to extract from calendar header
        header = soup.find('th', colspan=True) or soup.find('td', class_='banner')
        if header:
            header_text = header.get_text(strip=True).lower()
            # Turkish month names
            months_tr = {'ocak': 1, 'şubat': 2, 'mart': 3, 'nisan': 4, 'mayıs': 5, 'haziran': 6,
                        'temmuz': 7, 'ağustos': 8, 'eylül': 9, 'ekim': 10, 'kasım': 11, 'aralık': 12}
            # English month names
            months_en = {'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
                        'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12}
            
            for month_name, month_num in {**months_tr, **months_en}.items():
                if month_name in header_text:
                    current_month = month_num
                    break
            
            # Look for year
            import re
            year_match = re.search(r'20\d{2}', header_text)
            if year_match:
                current_year = int(year_match.group())
        
        # Find all day cells in calendar grid
        day_cells = soup.find_all('td', class_='days')
        
        for cell in day_cells:
            # Find the day number in this cell
            day_num_cell = cell.find('td', class_='days2')
            if not day_num_cell:
                continue
            
            try:
                day = int(day_num_cell.get_text(strip=True))
            except ValueError:
                continue
            
            # Check if this cell has event links
            event_links = cell.find_all('a', href=True)
            has_events = False
            
            for link in event_links:
                href = link.get('href', '')
                if 'eventresults.php?event=' in href:
                    has_events = True
                    break
            
            if has_events:
                # Date format: DD.MM.YYYY with detected month/year
                dates_with_events.append(f"{day:02d}.{current_month:02d}.{current_year}")
        
        return dates_with_events
    
    def get_database_dates(self):
        """
        Get list of dates already in database
        """
        try:
            with open('database.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error loading database: {e}")
            return set()
        
        dates = set()
        for record in data:
            tarih = record.get('Tarih')
            if tarih:
                dates.add(tarih)
        
        return dates
    
    def get_missing_dates(self, dates_with_events):
        """
        Find dates that have events but not yet in database
        """
        db_dates = self.get_database_dates()
        missing = [d for d in dates_with_events if d not in db_dates]
        return sorted(missing)
    
    def fetch_all_recent_dates(self, max_days=15):
        """
        Automatically fetch tournaments for recent dates that aren't in database
        
        Args:
            max_days: Maximum number of days to look back (default 15)
        """
        print(f"\n{'='*70}")
        print("AUTOMATIC TOURNAMENT DATA FETCHER")
        print(f"{'='*70}\n")
        
        # Get available dates from calendar
        print("1. Scanning Vugraph calendar for events...")
        available_dates = self.get_available_dates_from_calendar()
        print(f"   Found {len(available_dates)} dates with events")
        
        # Get dates already in database
        print("\n2. Checking database...")
        db_dates = self.get_database_dates()
        print(f"   Database has {len(db_dates)} unique dates")
        
        # Find missing dates
        print("\n3. Identifying new dates to fetch...")
        missing_dates = self.get_missing_dates(available_dates)
        print(f"   Found {len(missing_dates)} new date(s) to fetch: {missing_dates}")
        
        if not missing_dates:
            print("\n   ✓ Database is up to date!")
            return True
        
        # Fetch missing dates
        print(f"\n4. Fetching tournament data for {len(missing_dates)} date(s)...\n")
        
        success_count = 0
        error_count = 0
        
        for i, tarih in enumerate(missing_dates, 1):
            print(f"\n   [{i}/{len(missing_dates)}] Fetching {tarih}...")
            
            if self.fetcher.add_date_to_database(tarih):
                success_count += 1
                print(f"       ✓ Successfully added {tarih}")
            else:
                error_count += 1
                print(f"       ✗ Failed to add {tarih}")
        
        # Summary
        print(f"\n{'='*70}")
        print("SUMMARY")
        print(f"{'='*70}")
        print(f"Successfully fetched: {success_count} date(s)")
        print(f"Failed: {error_count} date(s)")
        print(f"Total records in database: {self._get_total_records()}")
        print(f"{'='*70}\n")
        
        return error_count == 0
    
    def _get_total_records(self):
        """Helper to get total records in database"""
        try:
            with open('database.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            return len(data)
        except:
            return 0


def main():
    """Main entry point"""
    fetcher = AutoTournamentFetcher()
    
    # Check for command line args
    if len(sys.argv) > 1:
        if sys.argv[1] == '--list':
            # Just list available/missing dates
            available = fetcher.get_available_dates_from_calendar()
            missing = fetcher.get_missing_dates(available)
            print("Available dates with events:")
            for d in available:
                status = "✓ in DB" if d not in fetcher.get_database_dates() else "  in DB"
                print(f"  {d} {status}")
            return 0
        
        elif sys.argv[1] == '--check':
            # Check for updates without fetching
            available = fetcher.get_available_dates_from_calendar()
            missing = fetcher.get_missing_dates(available)
            print(f"Total dates with events: {len(available)}")
            print(f"Missing from database: {len(missing)}")
            if missing:
                print(f"Dates to fetch: {missing}")
            return 0
    
    # Default: fetch all missing dates
    success = fetcher.fetch_all_recent_dates()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
