#!/usr/bin/env python3
"""Deploy to Fly.io using Machines API"""

import requests
import json
import os
from datetime import datetime

# Fly.io Machines API endpoint
FLY_API_BASE = "https://api.machines.dev/v1"
APP_NAME = "mgbric"
ORG_SLUG = "personal"

# Get token
token = os.environ.get('FLY_API_TOKEN')

if not token:
    print("❌ FLY_API_TOKEN not found in environment")
    print("\nSet it with:")
    print('  $env:FLY_API_TOKEN = "YOUR_TOKEN"')
    print('  (or copy from Fly.io dashboard → Account → Tokens)')
    exit(1)

print(f"🚀 Attempting Fly.io redeployment...")
print(f"   App: {APP_NAME}")
print(f"   Time: {datetime.now().isoformat()}")
print()

# Headers
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

try:
    # List machines
    print("📋 Fetching machine list...")
    url = f"{FLY_API_BASE}/apps/{APP_NAME}/machines"
    
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code != 200:
        print(f"❌ Error: HTTP {response.status_code}")
        print(f"   {response.text}")
        exit(1)
    
    machines = response.json()
    print(f"✅ Found {len(machines)} machine(s)")
    
    if not machines:
        print("❌ No machines found!")
        exit(1)
    
    # Get first machine
    machine = machines[0]
    machine_id = machine.get('id')
    
    print(f"🔄 Destroying machine {machine_id[:12]}...")
    
    # Destroy machine (Fly.io will auto-rebuild)
    url = f"{FLY_API_BASE}/apps/{APP_NAME}/machines/{machine_id}"
    response = requests.delete(url, headers=headers, timeout=10)
    
    if response.status_code in [200, 204]:
        print(f"✅ Machine destroyed successfully!")
        print("⏳ Fly.io will auto-create new machine in 30-60 seconds...")
        print("   New machine will have latest code from GitHub!")
    else:
        print(f"⚠️  Response: HTTP {response.status_code}")
        print(f"   {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
