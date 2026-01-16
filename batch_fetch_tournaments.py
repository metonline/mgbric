#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automatically fetch all tournament data from the 6 events
Uses the event IDs: 404155, 404197, 404275, 404377, 404426, 404498
"""

import sys
import subprocess
import json
import os
from datetime import datetime

# Event IDs with dates
EVENTS = [
    (404155, '2026-01-01'),
    (404197, '2026-01-02'),
    (404275, '2026-01-03'),
    (404377, '2026-01-04'),
    (404426, '2026-01-05'),
    (404498, '2026-01-06'),
]

def fetch_event_data(event_ids_str):
    """Call fetch_vugraph_hands.py with event IDs"""
    
    print("=" * 70)
    print("🚀 Automated Tournament Data Fetcher")
    print("=" * 70)
    
    print(f"\n📋 Events to fetch: {event_ids_str}")
    print("\n⏳ Fetching boards from Vugraph...")
    print("   (This may take a few minutes)\n")
    
    # Create input simulation for fetch_vugraph_hands.py
    # The script expects user input, so we'll create an interactive session
    
    script_path = r'C:\Users\metin\Desktop\BRIC\fetch_vugraph_hands.py'
    
    # Create a temporary script that runs fetch_vugraph_hands with automated input
    temp_script = r'C:\Users\metin\Desktop\BRIC\auto_fetch_wrapper.py'
    
    with open(temp_script, 'w', encoding='utf-8') as f:
        f.write(f'''#!/usr/bin/env python3
import subprocess
import sys

# Run fetch_vugraph_hands.py with event IDs as input
event_ids = "{event_ids_str}"

# Start the process
process = subprocess.Popen(
    [sys.executable, r'{script_path}'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Send event IDs and wait
stdout, stderr = process.communicate(input=event_ids + "\\n")

print(stdout)
if stderr:
    print(stderr, file=sys.stderr)

sys.exit(process.returncode)
''')
    
    # Run the wrapper
    result = subprocess.run(
        [sys.executable, temp_script],
        capture_output=False,
        text=True
    )
    
    # Clean up
    if os.path.exists(temp_script):
        os.remove(temp_script)
    
    return result.returncode == 0

def verify_database():
    """Verify the database was created and populated"""
    
    db_path = r'C:\Users\metin\Desktop\BRIC\app\www\hands_database.json'
    
    print(f"\n{'=' * 70}")
    print("✅ Database Verification")
    print(f"{'=' * 70}")
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return False
    
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            db = json.load(f)
        
        print(f"\n✅ Database loaded successfully!")
        print(f"   Total boards: {len(db)}")
        
        # Summary by date
        boards_by_date = {}
        for board_key, board_data in db.items():
            if isinstance(board_data, dict):
                date = board_data.get('date', 'unknown')
            else:
                date = 'unknown'
            
            if date not in boards_by_date:
                boards_by_date[date] = 0
            boards_by_date[date] += 1
        
        print(f"\n📊 Breakdown by Date:")
        for date in sorted(boards_by_date.keys()):
            print(f"   {date}: {boards_by_date[date]} boards")
        
        return True
    
    except Exception as e:
        print(f"❌ Error loading database: {e}")
        return False

def main():
    # Prepare event IDs
    event_ids = ','.join(str(e[0]) for e in EVENTS)
    
    print("\n🔍 Fetching Real Tournament Data from Vugraph")
    print("=" * 70)
    print(f"\nEvent IDs to fetch:")
    for event_id, date in EVENTS:
        print(f"  • {event_id} ({date})")
    
    # Fetch the data
    success = fetch_event_data(event_ids)
    
    # Verify
    if success:
        verify_database()
    else:
        print("\n⚠️  Fetch may have completed. Checking database...")
        verify_database()

if __name__ == '__main__':
    main()
