#!/usr/bin/env python3
"""
Disable GitHub Actions Workflow
When switching to webhook, disable the scheduled workflow to avoid duplicate updates
"""

import subprocess
import os
from datetime import datetime

def run_git_command(cmd, description=""):
    """Run a git command"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print(f"[OK] {description}")
            return True
        else:
            print(f"[ERROR] {description} failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"[ERROR] {description} error: {str(e)}")
        return False

def disable_workflow():
    """Disable GitHub Actions workflow"""
    
    print(f"\n{'='*70}")
    print("GitHub Actions Workflow Disabler")
    print(f"{'='*70}\n")
    
    workflow_file = ".github/workflows/update-from-vugraph.yml"
    
    if not os.path.exists(workflow_file):
        print(f"[WARNING] Workflow file not found: {workflow_file}")
        print("Create it first or run this from repository root")
        return False
    
    print(f"[INFO] Found workflow: {workflow_file}")
    
    # Read workflow file
    with open(workflow_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already disabled
    if "# name:" in content and not content.startswith("name:"):
        print("[INFO] Workflow is already disabled")
        return True
    
    # Disable by commenting out the first line
    lines = content.split('\n')
    if lines[0].startswith('name:'):
        lines[0] = f"# {lines[0]}"
        print("[INFO] Commenting out workflow name...")
    
    # Also comment out schedule if present
    for i, line in enumerate(lines):
        if line.strip().startswith('- cron:'):
            lines[i] = f"      # {line}"
            print(f"[INFO] Disabling cron: {line.strip()}")
    
    # Write back
    with open(workflow_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"[OK] Workflow disabled locally")
    
    # Git commit and push
    print(f"\n{'='*70}")
    print("Committing changes to GitHub")
    print(f"{'='*70}\n")
    
    if not run_git_command("git add .github/workflows/update-from-vugraph.yml", "Staging workflow file"):
        return False
    
    if not run_git_command(
        'git commit -m "Disable: Switch from GitHub Actions to webhook scheduler"',
        "Committing changes"
    ):
        print("[WARNING] Commit failed, but workflow is disabled locally")
    
    if not run_git_command("git push origin main", "Pushing to GitHub"):
        print("[WARNING] Push failed, but workflow is disabled locally")
    
    print(f"\n{'='*70}")
    print("[SUCCESS] Workflow disabled!")
    print(f"{'='*70}\n")
    print("Summary:")
    print("- GitHub Actions scheduled runs are now disabled")
    print("- Webhook server will handle automatic updates")
    print("- Next push to main branch will be handled by webhook\n")
    
    return True

if __name__ == '__main__':
    success = disable_workflow()
    exit(0 if success else 1)
