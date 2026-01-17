#!/usr/bin/env python3
"""Direct Fly.io deployment using Fly.io API"""

import requests
import os
import subprocess
import time

token = os.environ.get('FLY_API_TOKEN')
if not token:
    print("❌ FLY_API_TOKEN not set!")
    exit(1)

app_name = "mgbric"
api_base = "https://api.machines.dev/v1"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

print("🚀 Deploying to Fly.io directly...")
print(f"   App: {app_name}")
print()

# Step 1: Get app detail
print("📋 Getting app details...")
resp = requests.get(f"{api_base}/apps/{app_name}", headers=headers, timeout=10)

if resp.status_code != 200:
    print(f"❌ Can't get app details: HTTP {resp.status_code}")
    print(resp.text)
    exit(1)

print("✅ App exists")

# Step 2: Trigger remote builder to build Docker image
print("\n🔨 Building Docker image...")
print("   (Using Fly.io remote builder)")

# Use flyctl equivalent via API - deploy with --remote-only flag
# Since we don't have flyctl, we'll try creating a machine with the latest code

# Alternative: Use Fly Postgres deploy API or GraphQL
print("\n💡 Alternative approach: Create new machine from latest code")

# Get current machines
print("📋 Checking existing machines...")
resp = requests.get(f"{api_base}/apps/{app_name}/machines", headers=headers, timeout=10)

if resp.status_code == 200:
    machines = resp.json()
    print(f"   Found {len(machines)} machine(s)")
    
    for machine in machines:
        print(f"   - {machine['id'][:12]}: {machine.get('state', 'unknown')}")
else:
    print(f"   No machines found or error: {resp.status_code}")
    machines = []

# Since API deployment is complex without flyctl, let's just show what needs to happen
print("\n" + "="*60)
print("⚠️  GitHub Actions keeps failing - can't deploy this way")
print("\nAlternative: Use Fly.io Dashboard to manually deploy")
print("  1. Go to: https://fly.io/dashboard/mgbric")
print("  2. Click 'Launch an app instance'")
print("  3. Or check GitHub Actions errors in detail")
print("\n" + "="*60)
