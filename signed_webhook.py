#!/usr/bin/env python3
"""Direct webhook trigger with proper GitHub signature"""

import requests
import json
import hmac
import hashlib
import os

# Get webhook secret from environment or use a test value
webhook_secret = os.environ.get('GITHUB_WEBHOOK_SECRET', b'')

# Fly.io app webhook URL
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
        "message": "FIX: Update SCRIPT_VERSION constant to 379"
    }]
}

payload_json = json.dumps(payload)
payload_bytes = payload_json.encode('utf-8')

# Create signature
if webhook_secret:
    if isinstance(webhook_secret, str):
        webhook_secret = webhook_secret.encode('utf-8')
    signature = hmac.new(webhook_secret, payload_bytes, hashlib.sha256).hexdigest()
    signature_header = f"sha256={signature}"
else:
    signature_header = ""

headers = {
    "Content-Type": "application/json",
    "X-GitHub-Event": "push",
    "X-GitHub-Delivery": "12345-webhook-direct"
}

if signature_header:
    headers["X-Hub-Signature-256"] = signature_header

print("🔄 Production webhook trigger ediliyor (signed)...")
print(f"   URL: {webhook_url}")
if webhook_secret:
    print(f"   Signature: {signature_header[:20]}...")
else:
    print("   ⚠️  Webhook secret bulunamadı - signature boş")
print()

try:
    response = requests.post(webhook_url, data=payload_json, headers=headers, timeout=15)
    print(f"✅ Response: HTTP {response.status_code}")
    print(f"   Body: {response.text[:300]}")
    
    if response.status_code in [200, 204, 202]:
        print("\n✅ Webhook başarılı!")
        print("⏳ Production app git pull yapıyor...")
    
except Exception as e:
    print(f"❌ Hata: {str(e)}")
