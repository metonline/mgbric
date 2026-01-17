#!/usr/bin/env python3
import requests
import json

print("Testing API...")
try:
    response = requests.get('https://mgbric.fly.dev/api/data', timeout=10)
    data = response.json()
    
    print(f"✅ API Response OK (Status: {response.status_code})")
    print(f"   Records: {len(data.get('records', []))}")
    print(f"   Events: {len(data.get('events', {}))}")
    print(f"   Last Updated: {data.get('last_updated')}")
    
except Exception as e:
    print(f"❌ Error: {e}")
