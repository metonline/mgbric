#!/usr/bin/env python3
import requests

run_id = "21080567041"
url = f"https://api.github.com/repos/metonline/mgbric/actions/runs/{run_id}/jobs"

print("Fetching job details...")
resp = requests.get(url, timeout=10)

if resp.status_code == 200:
    jobs = resp.json().get('jobs', [])
    if jobs:
        job = jobs[0]
        print(f"\nJob: {job.get('name')}")
        print(f"Conclusion: {job.get('conclusion')}")
        print(f"\nSteps:")
        for step in job.get('steps', []):
            status = "✅" if step.get('conclusion') == 'success' else "❌"
            print(f"{status} {step.get('name')}: {step.get('conclusion')}")
else:
    print(f"Error: {resp.status_code}")
