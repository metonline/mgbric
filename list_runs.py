#!/usr/bin/env python3
import requests
url = 'https://api.github.com/repos/metonline/mgbric/actions/workflows/deploy-fly.yml/runs?per_page=5'
r = requests.get(url, timeout=10)
if r.status_code == 200:
    runs = r.json().get('workflow_runs', [])
    print('Latest workflow runs:\n')
    for i, run in enumerate(runs[:5], 1):
        status = run['status']
        conclusion = run.get('conclusion', 'N/A')
        created = run['created_at']
        run_id = run['id']
        print(f"{i}. Run {run_id}")
        print(f"   Status: {status} | Conclusion: {conclusion}")
        print(f"   Created: {created}")
        if status == 'in_progress':
            print(f"   🔄 RUNNING NOW!")
        print()
