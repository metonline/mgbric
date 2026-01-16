#!/usr/bin/env python3
"""
Sync database to GitHub automatically
Keeps your tournament data backed up and synced
"""

import json
import os
import subprocess
from datetime import datetime

def sync_database_to_github():
    """Commit and push database changes to GitHub"""
    
    print("🔄 Checking for database changes...")
    
    # Check git status
    result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
    changes = result.stdout.strip()
    
    if 'database.json' in changes or 'database.xlsx' in changes:
        print("✅ Database changes detected!")
        
        # Stage changes
        subprocess.run(['git', 'add', 'database.json', 'database.xlsx'])
        
        # Commit
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_msg = f"Auto-sync database - {timestamp}"
        subprocess.run(['git', 'commit', '-m', commit_msg])
        
        # Push
        result = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Database synced to GitHub!")
            return True
        else:
            print(f"❌ Push failed: {result.stderr}")
            return False
    else:
        print("ℹ️  No database changes to sync")
        return True

if __name__ == '__main__':
    sync_database_to_github()
