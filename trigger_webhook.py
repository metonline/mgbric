#!/usr/bin/env python3
"""Trigger webhook on production"""
import requests
import hmac
import hashlib
import json

SECRET = 'your-webhook-secret-here'
WEBHOOK_URL = 'https://mgbric.fly.dev/webhook'

payload = json.dumps({"ref": "refs/heads/main"})
payload_bytes = payload.encode('utf-8')

# Calculate signature
signature = 'sha256=' + hmac.new(
    SECRET.encode('utf-8'),
    payload_bytes,
    hashlib.sha256
).hexdigest()

headers = {
    'X-Hub-Signature-256': signature,
    'Content-Type': 'application/json'
}

print(f"🔑 Signature: {signature}")
print(f"📤 Sending webhook to {WEBHOOK_URL}...")

try:
    response = requests.post(WEBHOOK_URL, data=payload, headers=headers, timeout=30)
    print(f"✅ Status: {response.status_code}")
    print(f"📝 Response: {response.text[:200]}")
except Exception as e:
    print(f"❌ Error: {e}")
