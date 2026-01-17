#!/usr/bin/env python3
"""Trigger webhook with known secret"""

import requests
import json
import hmac
import hashlib

webhook_url = "https://mgbric.fly.dev/webhook"
webhook_secret = "your-webhook-secret-here"

payload = {
    "ref": "refs/heads/main",
    "repository": {"name": "mgbric", "full_name": "metonline/mgbric"},
    "pusher": {"name": "metonline"},
    "commits": [{"id": "0ea6b6c", "message": "v379 deploy"}]
}

payload_json = json.dumps(payload)
payload_bytes = payload_json.encode('utf-8')

signature = hmac.new(
    webhook_secret.encode('utf-8'), 
    payload_bytes, 
    hashlib.sha256
).hexdigest()

headers = {
    "Content-Type": "application/json",
    "X-GitHub-Event": "push",
    "X-Hub-Signature-256": f"sha256={signature}"
}

print("🚀 Production webhook trigger ediliyor...")
print(f"   Secret ile imzalanıyor...")
print()

try:
    response = requests.post(webhook_url, data=payload_json, headers=headers, timeout=20)
    print(f"✅ Response: HTTP {response.status_code}")
    print(f"   {response.text[:200]}")
    
    if response.status_code == 200:
        print("\n✅ SUCCESS! Webhook tetiklendi!")
        print("⏳ Production app git pull + restart yapıyor...")
        print("   30-60 saniye bekle, sayfayı refresh et (hard: Ctrl+Shift+Delete)")
    
except Exception as e:
    print(f"❌ Hata: {e}")
