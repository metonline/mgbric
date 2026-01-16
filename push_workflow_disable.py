#!/usr/bin/env python3
"""
Push changes to GitHub using subprocess
No Git CLI required - uses Python subprocess
"""

import subprocess
import os
from datetime import datetime

def execute(cmd, description=""):
    """Execute shell command"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {description}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        if result.returncode == 0:
            print(f"[OK] {description}")
            if result.stdout:
                print(result.stdout.strip())
            return True
        else:
            print(f"[ERROR] {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return False

def main():
    print(f"\n{'='*70}")
    print("Push GitHub Actions Disable to Repository")
    print(f"{'='*70}\n")
    
    # Check if git is available
    print("[INFO] Checking git availability...")
    result = subprocess.run("git --version", shell=True, capture_output=True)
    if result.returncode != 0:
        print("[ERROR] Git is not installed or not in PATH")
        print("\nManual solution:")
        print("1. Go to: https://github.com/USERNAME/BRIC/edit/main/.github/workflows/update-from-vugraph.yml")
        print("2. Make sure 'name:' is commented to '# name:'")
        print("3. Make sure all cron lines are commented")
        print("4. Click 'Commit changes'")
        print("5. Workflow will be disabled")
        return False
    
    print("[OK] Git found")
    
    # Stage changes
    if not execute("git add .github/workflows/update-from-vugraph.yml", "Staging workflow file"):
        return False
    
    # Commit
    if not execute(
        'git commit -m "Disable: Switch from GitHub Actions to webhook scheduler"',
        "Committing changes"
    ):
        print("[WARNING] Nothing to commit (already disabled)")
        return True
    
    # Push
    if not execute("git push origin main", "Pushing to GitHub"):
        return False
    
    print(f"\n{'='*70}")
    print("[SUCCESS] GitHub Actions disabled!")
    print(f"{'='*70}\n")
    print("""
Summary:
- GitHub Actions workflow is now disabled
- No more scheduled runs from GitHub
- Webhook will handle automatic updates
- Next push will trigger webhook (if configured)
""")
    
    return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
