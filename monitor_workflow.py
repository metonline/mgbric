#!/usr/bin/env python3
import json
import time
import subprocess
from datetime import datetime

def check_status():
    """Check database status and git log"""
    db = json.load(open('database.json', encoding='utf-8'))
    recs_today = len([r for r in db if r['Tarih'] == '16.01.2026'])
    hands_count = sum(1 for r in db if "Hands" in r)
    
    # Check for recent auto-updates
    result = subprocess.run(['git', 'log', '--oneline', '-1'], capture_output=True, text=True)
    latest_commit = result.stdout.strip()
    
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Database Status:")
    print(f"  Total records: {len(db)}")
    print(f"  Records for 16.01.2026: {recs_today}")
    print(f"  Records with hands: {hands_count}")
    print(f"  Latest commit: {latest_commit}")
    
    return recs_today > 0

print("🕐 Monitoring for workflow execution...")
print("⏳ Checking every 10 seconds (until 17:56 Turkey time)...")

for i in range(60):  # Check for up to 10 minutes
    if check_status():
        print("\n✅ NEW DATA DETECTED! Workflow completed successfully!")
        break
    time.sleep(10)
    
print("\nMonitoring complete.")
