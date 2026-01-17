#!/usr/bin/env python3
"""Direct webhook trigger for production app"""

import requests
import json

# Fly.io app webhook URL (from webhook_server.py logs or dashboard)
webhook_url = "https://mgbric.fly.dev/webhook"

# Minimal GitHub push event payload
payload = {
    "ref": "refs/heads/main",
    "repository": {
        "name": "mgbric",
        "full_name": "metonline/mgbric"
    },
    "pusher": {
        "name": "metonline"
    },
    "commits": [{
        "id": "0ea6b6c",
        "message": "FIX: Update SCRIPT_VERSION constant to 379",
        "timestamp": "2026-01-16T22:50:00Z"
    }]
}

headers = {
    "Content-Type": "application/json",
    "X-GitHub-Event": "push",
    "X-GitHub-Delivery": "12345-webhook"
}

print("🔄 Production webhook trigger ediliyor...")
print(f"   URL: {webhook_url}")
print()

try:
    response = requests.post(webhook_url, json=payload, headers=headers, timeout=15)
    print(f"✅ Response: HTTP {response.status_code}")
    print(f"   Body: {response.text[:200]}")
    
    if response.status_code in [200, 204]:
        print("\n✅ Webhook trigger başarılı!")
        print("⏳ Production app git pull + restart yapıyor...")
        print("   30-60 saniye bekle, sonra sayfayı refresh et")
    else:
        print(f"\n⚠️  Status {response.status_code} - Beklenen response")
        
except Exception as e:
    print(f"❌ Hata: {str(e)}")
    print("\n💡 Alternatif: Fly.io Dashboard'tan manual restart et")
    print("   https://fly.io/dashboard → mgbric → Settings → Restart")
