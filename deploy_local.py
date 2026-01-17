#!/usr/bin/env python3
"""Deploy app to Fly.io using official Fly.io machine API"""

import subprocess
import os
import sys

# Set the token from environment
token = os.environ.get('FLY_API_TOKEN')

if not token:
    print("❌ FLY_API_TOKEN not set!")
    sys.exit(1)

# Configure flyctl
print("🔧 Configuring flyctl...")
subprocess.run(['flyctl', 'auth', 'login', '--token', token], 
               capture_output=True)

# Deploy
print("\n🚀 Deploying to Fly.io...")
result = subprocess.run(
    ['flyctl', 'deploy', '--remote-only', '--app', 'mgbric', '-v'],
    env={**os.environ, 'FLY_API_TOKEN': token}
)

if result.returncode == 0:
    print("\n✅ Deployment successful!")
    print("⏳ Machine will be ready in 1-2 minutes")
else:
    print("\n❌ Deployment failed!")
    sys.exit(1)
