#!/usr/bin/env python3
"""Create and deploy machine on Fly.io using Machines API"""

import requests
import json
import os
from datetime import datetime

FLY_API_BASE = "https://api.machines.dev/v1"
APP_NAME = "mgbric"

token = os.environ.get('FLY_API_TOKEN')

if not token:
    print("❌ FLY_API_TOKEN not found")
    exit(1)

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

print(f"🚀 Creating machine on Fly.io...")
print(f"   App: {APP_NAME}")
print()

# Machine configuration
machine_config = {
    "config": {
        "image": "registry.fly.io/mgbric:deployment-0fd0c3e",
        "env": {
            "GITHUB_WEBHOOK_SECRET": "your-webhook-secret-here"
        },
        "services": [
            {
                "ports": [
                    {
                        "port": 80,
                        "handlers": ["http"]
                    },
                    {
                        "port": 443,
                        "handlers": ["tls", "http"]
                    }
                ],
                "protocol": "tcp",
                "internal_port": 8080
            }
        ]
    },
    "region": "ams"
}

try:
    print("📦 Building image...")
    url = f"{FLY_API_BASE}/apps/{APP_NAME}/machines"
    
    response = requests.post(url, json=machine_config, headers=headers, timeout=120)
    
    print(f"Response: HTTP {response.status_code}")
    
    if response.status_code in [200, 201]:
        machine = response.json()
        machine_id = machine.get('id')
        print(f"\n✅ Machine created: {machine_id[:12]}")
        print("⏳ Machine is starting...")
        print("   This may take 1-2 minutes")
        print("\nOnce ready, hard refresh: mgbric.fly.dev (Ctrl+Shift+Delete)")
    else:
        print(f"Response: {response.text[:500]}")
        
        # If image doesn't exist, try with latest Docker image
        if "not found" in response.text.lower():
            print("\n💡 Trying with latest Docker image...")
            machine_config["config"]["image"] = "registry.fly.io/mgbric:latest"
            response = requests.post(url, json=machine_config, headers=headers, timeout=120)
            print(f"Second attempt: HTTP {response.status_code}")
            print(response.text[:300])
        
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
