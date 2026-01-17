#!/usr/bin/env python3
import requests

# Get logs from latest failed run
run_id = "21080247406"
url = f"https://api.github.com/repos/metonline/mgbric/actions/runs/{run_id}/logs"

print("📋 Attempting to get workflow logs...\n")

try:
    response = requests.get(url, timeout=10, allow_redirects=True)
    
    if response.status_code == 200:
        # Logs are usually in zip format, try to read text
        print(response.text[:1500])
    elif response.status_code == 302:
        # Redirect to logs location
        print(f"Logs available at redirect URL")
        print(f"Status: {response.status_code}")
    else:
        print(f"Status: {response.status_code}")
        print(f"Try visiting: https://github.com/metonline/mgbric/actions/runs/{run_id}")
        
except Exception as e:
    print(f"Error: {e}")
    print(f"\nManually check logs at:")
    print(f"https://github.com/metonline/mgbric/actions/runs/{run_id}")
