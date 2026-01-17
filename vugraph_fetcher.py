#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import sys
import os

class VugraphDataFetcher:
    """
    Practical tool to fetch tournament data from Vugraph and add to database
    Handles both NS (Kuzey-Güney) and EW (Doğu-Batı) sections correctly
    """
    
    BASE_URL = "https://clubs.vugraph.com/hosgoru"
    DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.json')
    
    def __init__(self):
        self.records_added = []
        self.errors = []
    
    def fetch_calendar(self):
        """Fetch all tournaments from Vugraph calendar"""
        try:
            response = requests.get(f"{self.BASE_URL}/calendar.php", timeout=30)
            response.encoding = 'iso-8859-9'  # Turkish encoding
            response.raise_for_status()
            return response.text
        except Exception as e:
            self.errors.append(f"Failed to fetch calendar: {e}")
            return None
    
    def parse_calendar_for_date(self, html, target_date_str):
        """
        Parse calendar grid to find events for a specific date
        Calendar structure: Each day cell contains day number and event links
        target_date_str format: "29.12.2025"
        
        Returns list of events for that specific date
        """
        soup = BeautifulSoup(html, 'html.parser')
        events = []
        
        # Extract target day from date string (format: "29.12.2025")
        day_number = int(target_date_str.split('.')[0])
        
        # Find all day cells in calendar grid
        day_cells = soup.find_all('td', class_='days')
        
        for cell in day_cells:
            # Find the day number in this cell
            day_num_cell = cell.find('td', class_='days2')
            if not day_num_cell:
                continue
            
            try:
                cell_day = int(day_num_cell.get_text(strip=True))
            except ValueError:
                continue
            
            # Check if this is the target day
            if cell_day == day_number:
                # Find all event links in this cell
                event_links = cell.find_all('a', href=True)
                for link in event_links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    if 'eventresults.php?event=' in href:
                        event_id = href.split('event=')[1]
                        events.append({
                            'id': event_id,
                            'name': text,
                            'url': href,
                            'date': target_date_str,
                            'day': day_number
                        })
        
        return events
    
    def parse_event_results(self, event_id, turnuva_name, tarih):
        """
        Parse both NS and EW sections from a single tournament event
        Returns: list of records
        """
        url = f"{self.BASE_URL}/eventresults.php?event={event_id}"
        
        try:
            response = requests.get(url, timeout=30)
            response.encoding = 'utf-8'  # Ensure UTF-8 decoding
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            records = []
            current_direction = None
            
            # Find the main results table (class="colored")
            tables = soup.find_all('table', class_='colored')
            
            if not tables:
                self.errors.append(f"Event {event_id}: No results table found")
                return []
            
            table = tables[0]
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if not cells:
                    continue
                
                # Detect direction header rows (single cell)
                if len(cells) == 1:
                    text = cells[0].get_text(strip=True)
                    if 'Kuzey' in text or 'North' in text:
                        current_direction = 'NS'
                    elif 'Doğu' in text or 'Bati' in text or 'East' in text:
                        current_direction = 'EW'
                    continue
                
                # Skip column header rows
                if len(cells) >= 3:
                    first_cell = cells[0].get_text(strip=True)
                    if first_cell in ['Sıra', 'Sira', 'Rank']:
                        continue
                
                # Parse data row
                if len(cells) >= 3 and current_direction:
                    try:
                        sira_text = cells[0].get_text(strip=True)
                        pair_text = cells[1].get_text(strip=True)
                        skor_text = cells[2].get_text(strip=True)
                        
                        # Parse rank
                        try:
                            sira = int(sira_text)
                        except ValueError:
                            continue
                        
                        # Parse score
                        skor = float(skor_text.replace(',', '.'))
                        
                        # Parse pair names
                        pair_parts = pair_text.split(' - ')
                        if len(pair_parts) >= 2:
                            oyuncu1 = pair_parts[0].strip()
                            oyuncu2 = ' - '.join(pair_parts[1:]).strip()
                            
                            record = {
                                'Sıra': sira,
                                'Tarih': tarih,
                                'Oyuncu 1': oyuncu1,
                                'Oyuncu 2': oyuncu2,
                                'Skor': skor,
                                'Direction': current_direction,
                                'Turnuva': turnuva_name,
                                'Link': url
                            }
                            records.append(record)
                    
                    except (ValueError, IndexError):
                        continue
            
            return records
        
        except Exception as e:
            self.errors.append(f"Event {event_id}: {e}")
            return []
    
    def add_date_to_database(self, tarih):
        """
        Main method: Fetch and add all tournament data for a specific date
        tarih format: "29.12.2025"
        Now handles new database format (dict with events)
        """
        print(f"\n{'='*60}")
        print(f"Fetching data for: {tarih}")
        print(f"{'='*60}\n")
        
        # Load current database
        try:
            with open(self.DB_FILE, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
        except Exception as e:
            self.errors.append(f"Failed to load database: {e}")
            return False
        
        # Initialize if new format
        if isinstance(data, list):
            # Convert old format to new - PRESERVE OLD DATA!
            old_records = data  # Save old array
            data = {
                "version": "2.0",
                "last_updated": datetime.now().isoformat(),
                "events": {},
                "metadata": {"total_tournaments": 0, "total_boards": 0},
                "legacy_records": old_records  # Keep all old records for compatibility
            }
            print(f"   [INFO] Converted old format: saved {len(old_records)} legacy records")
        elif not isinstance(data, dict) or 'events' not in data:
            data = {
                "version": "2.0",
                "last_updated": datetime.now().isoformat(),
                "events": {},
                "metadata": {"total_tournaments": 0, "total_boards": 0}
            }
        
        # Fetch calendar
        print("1. Fetching Vugraph calendar...")
        calendar_html = self.fetch_calendar()
        if not calendar_html:
            return False
        
        # Parse events for this date
        print("2. Parsing calendar events...")
        events = self.parse_calendar_for_date(calendar_html, tarih)
        print(f"   Found {len(events)} total events")
        
        if not events:
            self.errors.append("No events found in calendar")
            return False
        
        print(f"\n3. Fetching tournament data...")
        print(f"   Found {len(events)} event(s) for {tarih}")
        
        # Process all events for this date
        for event in events:
            print(f"\n   Event {event['id']}: {event['name']}")
            
            # Construct tournament name with date
            turnuva_name = f"{event['name']} Sonuçları ({tarih} 14:00)"
            
            # Parse event
            records = self.parse_event_results(event['id'], turnuva_name, tarih)
            
            if records:
                ns_count = len([r for r in records if r.get('Direction') == 'NS'])
                ew_count = len([r for r in records if r.get('Direction') == 'EW'])
                print(f"   ✓ Parsed {len(records)} records (NS: {ns_count}, EW: {ew_count})")
                
                # Store in new format
                event_key = f"event_{event['id']}"
                data['events'][event_key] = {
                    'id': event['id'],
                    'name': turnuva_name,
                    'date': tarih,
                    'results': {
                        'NS': [r for r in records if r.get('Direction') == 'NS'],
                        'EW': [r for r in records if r.get('Direction') == 'EW']
                    }
                }
                self.records_added.extend(records)
            else:
                print(f"   ✗ No records found")
        
        if not self.records_added:
            self.errors.append("No records could be parsed from any event")
            return False
        
        # Update metadata
        print(f"\n4. Updating database...")
        data['last_updated'] = datetime.now().isoformat()
        data['metadata']['total_tournaments'] = len(data['events'])
        
        # Save database (UTF-8 without BOM)
        try:
            with open(self.DB_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"\n   ✓ Database saved successfully")
        except Exception as e:
            self.errors.append(f"Failed to save database: {e}")
            return False
        
        # Verify
        print(f"\n5. Verification:")
        # Handle both old and new format
        if isinstance(data, dict) and 'events' in data:
            # New format
            all_records = []
            for event_data in data.get('events', {}).values():
                if 'results' in event_data:
                    all_records.extend(event_data['results'].get('NS', []))
                    all_records.extend(event_data['results'].get('EW', []))
            verify = [r for r in all_records if r.get('Tarih') == tarih]
        else:
            # Old format (array) - shouldn't happen but handle it
            verify = [r for r in data if isinstance(r, dict) and r.get('Tarih') == tarih]
        
        verify_ns = [r for r in verify if r.get('Direction') == 'NS']
        verify_ew = [r for r in verify if r.get('Direction') == 'EW']
        print(f"   {tarih}: {len(verify)} total records")
        print(f"   NS pairs: {len(verify_ns)}")
        print(f"   EW pairs: {len(verify_ew)}")
        
        # Show by tournament
        tournaments = {}
        for r in verify:
            t = r.get('Turnuva')
            tournaments[t] = tournaments.get(t, 0) + 1
        
        print(f"\n   Tournaments for {tarih}:")
        for t, count in tournaments.items():
            print(f"   • {t}: {count} records")
        
        return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python vugraph_fetcher.py <date>")
        print("Example: python vugraph_fetcher.py 29.12.2025")
        sys.exit(1)
    
    tarih = sys.argv[1]
    
    # Validate date format
    try:
        datetime.strptime(tarih, "%d.%m.%Y")
    except ValueError:
        print(f"Invalid date format: {tarih}")
        print("Use format: DD.MM.YYYY (e.g., 29.12.2025)")
        sys.exit(1)
    
    fetcher = VugraphDataFetcher()
    success = fetcher.add_date_to_database(tarih)
    
    # Show errors if any
    if fetcher.errors:
        print(f"\n{'='*60}")
        print("WARNINGS/ERRORS:")
        for error in fetcher.errors:
            print(f"  [WARNING] {error}")
        print(f"{'='*60}")
    
    if success:
        print(f"\n[OK] Data for {tarih} successfully updated!")
        return 0
    else:
        print(f"\n✗ Failed to fetch data for {tarih}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
