#!/usr/bin/env python3
"""
Webhook Cron Runner - Keep webhook server running on shared hosting
Run this every 5 minutes via cPanel Cron Jobs
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

# Configuration
WEBHOOK_DIR = os.path.dirname(os.path.abspath(__file__))
WEBHOOK_SERVER = os.path.join(WEBHOOK_DIR, 'webhook_server.py')
WEBHOOK_LOG = os.path.join(WEBHOOK_DIR, 'webhook_cron.log')
PID_FILE = os.path.join(WEBHOOK_DIR, 'webhook.pid')

def log_message(msg):
    """Log message to file"""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    with open(WEBHOOK_LOG, 'a') as f:
        f.write(f"[{timestamp}] {msg}\n")

def is_process_running(pid):
    """Check if process is still running"""
    if not os.path.exists(PID_FILE):
        return False
    
    try:
        with open(PID_FILE, 'r') as f:
            stored_pid = int(f.read().strip())
        
        # Try to check if process exists
        os.kill(stored_pid, 0)
        return True
    except:
        return False

def start_webhook_server():
    """Start webhook server in background"""
    
    log_message("Checking webhook server status...")
    
    # Check if already running
    if is_process_running(int(open(PID_FILE).read().strip() if os.path.exists(PID_FILE) else 0)):
        log_message("Webhook server already running")
        return
    
    log_message("Starting webhook server...")
    
    try:
        # Start Flask server in background
        process = subprocess.Popen(
            [sys.executable, WEBHOOK_SERVER],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=WEBHOOK_DIR,
            preexec_fn=os.setsid if hasattr(os, 'setsid') else None
        )
        
        # Save PID
        with open(PID_FILE, 'w') as f:
            f.write(str(process.pid))
        
        log_message(f"Webhook server started (PID: {process.pid})")
        
    except Exception as e:
        log_message(f"Error starting webhook server: {e}")

def check_and_update_database():
    """Check and update database if needed"""
    
    log_message("Checking for pending updates...")
    
    try:
        auto_update = os.path.join(WEBHOOK_DIR, 'auto_update_vugraph.py')
        
        if os.path.exists(auto_update):
            # Run auto-update script
            result = subprocess.run(
                [sys.executable, auto_update],
                cwd=WEBHOOK_DIR,
                capture_output=True,
                timeout=60
            )
            
            if result.returncode == 0:
                log_message("Database update completed successfully")
            else:
                log_message(f"Database update failed: {result.stderr.decode()}")
    
    except Exception as e:
        log_message(f"Error during database check: {e}")

if __name__ == '__main__':
    try:
        log_message("="*70)
        log_message("Webhook Cron Runner started")
        
        # Start webhook server if not running
        start_webhook_server()
        
        # Check and update database
        check_and_update_database()
        
        log_message("Cron job completed")
        log_message("="*70)
        
    except Exception as e:
        log_message(f"FATAL ERROR: {e}")
        import traceback
        log_message(traceback.format_exc())
