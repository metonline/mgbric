#!/usr/bin/env python3
"""Check GitHub Actions workflow status"""

import requests

owner = "metonline"
repo = "mgbric"
workflow = "deploy-fly.yml"

print("🔍 Checking GitHub Actions status...\n")

# Get latest workflow runs (no auth needed for public repos)
url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow}/runs"

try:
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        runs = data.get('workflow_runs', [])
        
        if runs:
            latest = runs[0]
            print(f"Latest workflow run:")
            print(f"  ID: {latest['id']}")
            print(f"  Status: {latest['status']}")
            print(f"  Conclusion: {latest.get('conclusion', 'N/A')}")
            print(f"  Created: {latest['created_at']}")
            print(f"  Updated: {latest['updated_at']}")
            
            if latest['status'] == 'completed' and latest['conclusion'] == 'failure':
                print(f"\n❌ Workflow FAILED!")
                print(f"   Check logs: {latest['html_url']}/attempts/1")
            elif latest['status'] == 'in_progress':
                print(f"\n⏳ Workflow still RUNNING...")
                print(f"   Check progress: {latest['html_url']}")
            elif latest['status'] == 'completed' and latest['conclusion'] == 'success':
                print(f"\n✅ Workflow SUCCEEDED!")
                print(f"   Machine should be deploying now...")
            else:
                print(f"\n⚠️  Status: {latest['status']} / {latest.get('conclusion')}")
        else:
            print("❌ No workflow runs found!")
            print(f"   Check: https://github.com/{owner}/{repo}/actions")
            
    else:
        print(f"❌ API Error: HTTP {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")
