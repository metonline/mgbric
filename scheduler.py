#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Update Scheduler
- Runs at 00:00 (midnight)
- Runs at 10:00 (10 AM)
- Runs every 5 minutes between 17:00-18:00 (5 PM - 6 PM)
"""

import os
import sys
import json
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

# Set stdout encoding for Windows compatibility
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class DatabaseScheduler:
    def __init__(self, repo_path=None):
        self.repo_path = repo_path or os.path.dirname(os.path.abspath(__file__))
        self.scheduler = BackgroundScheduler()
        self.scheduler.daemon = True
        
    def update_database(self):
        """Update database from Vugraph"""
        try:
            from vugraph_fetcher import VugraphDataFetcher
            
            print(f"\n{'='*60}")
            print(f"[{datetime.now()}] [REFRESH] Scheduled Database Update Starting...")
            print(f"{'='*60}")
            
            fetcher = VugraphDataFetcher()
            
            # Get dates to fetch (last 3 days + next 7 days)
            today = datetime.now()
            start_date_obj = today - timedelta(days=3)
            end_date_obj = today + timedelta(days=7)
            
            print(f"[{datetime.now()}] Fetching tournaments from {start_date_obj.strftime('%d.%m.%Y')} to {end_date_obj.strftime('%d.%m.%Y')}")
            
            # Fetch data for each date in range
            current_date = start_date_obj
            success_count = 0
            
            while current_date <= end_date_obj:
                date_str = current_date.strftime('%d.%m.%Y')
                try:
                    if fetcher.add_date_to_database(date_str):
                        success_count += 1
                except Exception as date_err:
                    print(f"[{datetime.now()}] [WARN] Failed to fetch {date_str}: {str(date_err)}")
                
                current_date += timedelta(days=1)
            
            if success_count > 0:
                print(f"[{datetime.now()}] [OK] Database updated successfully ({success_count} dates processed)")
                
                # Log the update
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'status': 'success',
                    'dates_processed': success_count
                }
                self.log_update(log_entry)
            else:
                print(f"[{datetime.now()}] [FAIL] Database update failed (0 dates processed)")
            
            # After updating tournament data, fetch hands for new tournaments
            print(f"\n[{datetime.now()}] [HANDS] Starting hands fetching for 2026+ tournaments...")
            self.fetch_tournament_hands()
            
            return True
                
        except Exception as e:
            print(f"[{datetime.now()}] [ERROR] Error during database update: {str(e)}")
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'error': str(e)
            }
            self.log_update(log_entry)
            return False
        finally:
            print(f"{'='*60}\n")
    
    def log_update(self, entry):
        """Log update to scheduler log file"""
        try:
            log_file = os.path.join(self.repo_path, 'scheduler_log.json')
            logs = []
            
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            
            logs.append(entry)
            
            # Keep only last 100 entries
            logs = logs[-100:]
            
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            print(f"[{datetime.now()}] [WARN] Error logging update: {str(e)}")
    
    def start(self):
        """Start the scheduler"""
        try:
            print(f"\n{'='*60}")
            print("Starting Database Scheduler...")
            print(f"{'='*60}")
            
            # Schedule at 00:00 (midnight)
            self.scheduler.add_job(
                self.update_database,
                CronTrigger(hour=0, minute=0),
                id='update_midnight',
                name='Database Update at Midnight (00:00)',
                replace_existing=True
            )
            print("[OK] Scheduled: 00:00 (Midnight)")
            
            # Schedule at 10:00
            self.scheduler.add_job(
                self.update_database,
                CronTrigger(hour=10, minute=0),
                id='update_10am',
                name='Database Update at 10:00 AM',
                replace_existing=True
            )
            print("[OK] Scheduled: 10:00 (10 AM)")
            
            # Schedule every 5 minutes between 17:00 and 18:00 (5 PM - 6 PM)
            # This will run at: 17:00, 17:05, 17:10, 17:15, 17:20, 17:25, 17:30, 17:35, 17:40, 17:45, 17:50, 17:55
            self.scheduler.add_job(
                self.update_database,
                CronTrigger(hour=17, minute='0-55/5'),
                id='update_evening',
                name='Database Update Every 5 Minutes (17:00-17:55)',
                replace_existing=True
            )
            print("[OK] Scheduled: Every 5 minutes from 17:00 to 17:55 (5 PM - 6 PM)")
            
            self.scheduler.start()
            print(f"{'='*60}")
            print("[OK] Scheduler started successfully!")
            print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"[ERROR] Error starting scheduler: {str(e)}")
            raise
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("[Scheduler] Stopped")
    
    def get_jobs(self):
        """Get list of scheduled jobs"""
        return self.scheduler.get_jobs()

    def fetch_tournament_hands(self):
        """Fetch hands for tournaments from 2026+ that don't have hands yet"""
        try:
            import requests
            from bs4 import BeautifulSoup
            from collections import defaultdict
            from urllib.parse import urlparse, parse_qs
            import re
            
            print(f"[{datetime.now()}] Loading database...")
            db_path = os.path.join(self.repo_path, 'database.json')
            with open(db_path, 'r', encoding='utf-8') as f:
                database = json.load(f)
            
            # Group tournaments and check which need hands
            tournaments_need_hands = defaultdict(list)
            cutoff_date = datetime.strptime('01.01.2026', '%d.%m.%Y')
            
            for idx, record in enumerate(database):
                # Skip records that already have hands
                if 'Hands' in record:
                    continue
                
                # Filter by date - only 2026 onwards
                date_str = record.get('Tarih', '')
                try:
                    record_date = datetime.strptime(date_str, '%d.%m.%Y')
                    if record_date < cutoff_date:
                        continue
                except:
                    continue
                
                # Extract event ID
                link = record.get('Link', '')
                try:
                    parsed = urlparse(link)
                    params = parse_qs(parsed.query)
                    event_id = params.get('event', [None])[0]
                    if event_id:
                        tournaments_need_hands[event_id].append(idx)
                except:
                    continue
            
            if not tournaments_need_hands:
                print(f"[{datetime.now()}] [OK] All tournaments already have hands")
                return True
            
            print(f"[{datetime.now()}] [HANDS] Found {len(tournaments_need_hands)} tournaments needing hands")
            
            # Fetch hands for up to 3 tournaments per scheduled run (to avoid timeouts)
            hands_fetched = 0
            for event_id, record_indices in list(tournaments_need_hands.items())[:3]:
                try:
                    print(f"[{datetime.now()}] Fetching hands for event {event_id}...")
                    hands = self._fetch_event_hands(event_id)
                    
                    if hands:
                        for idx in record_indices:
                            database[idx]['Hands'] = hands
                            database[idx]['HandsFetched'] = True
                        hands_fetched += 1
                        print(f"[{datetime.now()}] [OK] Fetched {len(hands)} boards")
                    else:
                        print(f"[{datetime.now()}] [WARN] Failed to fetch hands for event {event_id}")
                    
                    # Rate limiting
                    import time
                    time.sleep(2)
                except Exception as e:
                    print(f"[{datetime.now()}] [ERROR] Error fetching hands: {str(e)[:50]}")
                    continue
            
            # Save updated database
            if hands_fetched > 0:
                with open(db_path, 'w', encoding='utf-8') as f:
                    json.dump(database, f, ensure_ascii=False, indent=2)
                print(f"[{datetime.now()}] [OK] Hands database saved ({hands_fetched} tournaments)")
                return True
            
            return False
            
        except Exception as e:
            print(f"[{datetime.now()}] [ERROR] Error in hands fetching: {str(e)}")
            return False
    
    def _fetch_event_hands(self, event_id, num_boards=30):
        """Fetch hands for a single event"""
        try:
            import requests
            from bs4 import BeautifulSoup
            import re
            import time
            
            hands_by_board = {}
            
            for board_num in range(1, num_boards + 1):
                try:
                    url = f"https://clubs.vugraph.com/hosgoru/boardsummary.php?event={event_id}&board={board_num}"
                    response = requests.get(url, timeout=5)
                    response.encoding = 'utf-8'
                    soup = BeautifulSoup(response.content, 'html.parser')
                    board_text = soup.get_text()
                    
                    hands = {}
                    for direction in ['North', 'South', 'East', 'West']:
                        patterns = [
                            rf"{direction}\s*[:\s]+([AKQJT2-9]*(?:\s+[AKQJT2-9]*)*)",
                            rf"{direction.lower()}.*?[:\s]+([AKQJT2-9]+)",
                        ]
                        
                        hand_found = None
                        for pattern in patterns:
                            match = re.search(pattern, board_text, re.IGNORECASE)
                            if match:
                                hand_found = match.group(1)
                                break
                        
                        if hand_found:
                            hands[direction[0]] = self._parse_hand_string(hand_found)
                        else:
                            hands[direction[0]] = {'S': '', 'H': '', 'D': '', 'C': ''}
                    
                    if any(hands.values()):
                        hands_by_board[str(board_num)] = hands
                    
                    time.sleep(0.3)
                except:
                    time.sleep(0.3)
                    continue
            
            return hands_by_board if hands_by_board else None
        except:
            return None
    
    def _parse_hand_string(self, hand_str):
        """Parse hand string to dict"""
        if not hand_str or hand_str.strip() in ['-', '']:
            return {'S': '', 'H': '', 'D': '', 'C': ''}
        
        result = {}
        hand_str = hand_str.strip()
        
        if ':' in hand_str:
            for suit_part in hand_str.split():
                if ':' in suit_part:
                    suit, cards = suit_part.split(':')
                    result[suit.upper()] = cards
        else:
            suits = ['S', 'H', 'D', 'C']
            current_suit = 0
            current_cards = ''
            
            for char in hand_str:
                if char in suits:
                    if current_cards:
                        result[suits[current_suit]] = current_cards
                        current_cards = ''
                    current_suit = suits.index(char)
                else:
                    current_cards += char
            
            if current_cards:
                result[suits[current_suit]] = current_cards
        
        return {s: result.get(s, '') for s in ['S', 'H', 'D', 'C']}

if __name__ == '__main__':
    scheduler = DatabaseScheduler()
    scheduler.start()
    
    # Keep running
    try:
        while True:
            pass
    except KeyboardInterrupt:
        scheduler.stop()
