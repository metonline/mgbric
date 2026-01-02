#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple scheduler for automatic tournament data fetching
Run in background to check for new data periodically
"""

import time
import schedule
import sys
from datetime import datetime
from pathlib import Path
from auto_fetch_tournaments import AutoTournamentFetcher

class TournamentScheduler:
    """
    Background scheduler for tournament data fetching
    """
    
    def __init__(self, check_interval_hours=6):
        self.fetcher = AutoTournamentFetcher()
        self.check_interval = check_interval_hours
        self.running = False
        
    def fetch_job(self):
        """Job to run automatically"""
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running automatic tournament fetch...")
        try:
            self.fetcher.fetch_all_recent_dates()
        except Exception as e:
            print(f"Error during fetch: {e}")
    
    def start(self, check_times=None):
        """
        Start the scheduler
        
        Args:
            check_times: Times to run daily checks (list of "HH:MM" format strings)
                        Default: ["10:30", "18:00", "23:45"]
        """
        if check_times is None:
            check_times = ["10:30", "18:00", "23:45"]
        
        print(f"\n{'='*70}")
        print("TOURNAMENT DATA SCHEDULER STARTED")
        print(f"{'='*70}")
        print(f"Daily checks scheduled for: {', '.join(check_times)}")
        print(f"Additional checks every {self.check_interval} hours")
        print("\nScheduler is running. Press Ctrl+C to stop.\n")
        
        # Schedule daily at specific times
        for check_time in check_times:
            schedule.every().day.at(check_time).do(self.fetch_job)
        
        # Also check every N hours
        schedule.every(self.check_interval).hours.do(self.fetch_job)
        
        self.running = True
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute if a job needs to run
        except KeyboardInterrupt:
            print("\n\n✓ Scheduler stopped.")
            self.running = False


def main():
    """Main entry point"""
    
    print(f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║              TOURNAMENT DATA AUTOMATIC SCHEDULER                          ║
║                                                                           ║
║  This tool runs in the background and periodically fetches new          ║
║  tournament data from Vugraph.                                           ║
║                                                                           ║
║  Press Ctrl+C to stop the scheduler                                      ║
╚═══════════════════════════════════════════════════════════════════════════╝
""")
    
    # Default check times (3 times per day)
    check_times = ["10:30", "18:00", "23:45"]
    check_interval = 6    # Default: every 6 hours
    
    # Parse command line arguments
    # Usage: python background_fetch_scheduler.py [times] [interval]
    # Example: python background_fetch_scheduler.py "10:30,18:00,23:45" 6
    if len(sys.argv) > 1:
        times_arg = sys.argv[1]
        if "," in times_arg:
            check_times = [t.strip() for t in times_arg.split(",")]
        else:
            check_times = [times_arg]
    
    if len(sys.argv) > 2:
        try:
            check_interval = int(sys.argv[2])
        except ValueError:
            print(f"Invalid interval: {sys.argv[2]}")
            sys.exit(1)
    
    # Validate time format
    for check_time in check_times:
        try:
            datetime.strptime(check_time, "%H:%M")
        except ValueError:
            print(f"Invalid time format: {check_time}")
            print("Use format: HH:MM (e.g., 10:30)")
            sys.exit(1)
    
    # Start scheduler
    scheduler = TournamentScheduler(check_interval_hours=check_interval)
    scheduler.start(check_times=check_times)


if __name__ == "__main__":
    # Check if schedule package is installed
    try:
        import schedule
    except ImportError:
        print("Error: 'schedule' package not installed.")
        print("Install it with: pip install schedule")
        sys.exit(1)
    
    sys.exit(main())
