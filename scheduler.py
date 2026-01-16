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
                return True
            else:
                print(f"[{datetime.now()}] [FAIL] Database update failed (0 dates processed)")
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'status': 'failed',
                    'date_range': f"{start_date} to {end_date}"
                }
                self.log_update(log_entry)
                return False
                
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


if __name__ == '__main__':
    scheduler = DatabaseScheduler()
    scheduler.start()
    
    # Keep running
    try:
        while True:
            pass
    except KeyboardInterrupt:
        scheduler.stop()
