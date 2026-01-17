#!/usr/bin/env python3
"""Trigger GitHub Actions workflow manually"""

import requests
import json
import os

# We need a GitHub token to trigger workflows
# Since we don't have one, let's try a different approach:
# Just make a commit to database.json to trigger the workflow

print("🔄 Triggering GitHub Actions via Git commit...")
print("\nTo manually trigger: https://github.com/metonline/mgbric/actions")
print("Select 'Deploy to Fly.io' → 'Run workflow' → select 'main' branch")
print("\nOr use GitHub CLI: gh workflow run deploy-fly.yml --ref main")
