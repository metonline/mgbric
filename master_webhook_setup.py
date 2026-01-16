#!/usr/bin/env python3
"""
Master Webhook Setup Script
Complete one-step setup: webhook + GitHub config + disable GitHub Actions
"""

import os
import sys
import subprocess
import json
from datetime import datetime

def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(text.center(70))
    print(f"{'='*70}\n")

def print_section(text):
    """Print section header"""
    print(f"\n[*] {text}")
    print("-" * len(text))

def run_command(cmd, description=""):
    """Run a command"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr
    except Exception as e:
        return False, str(e)

def main():
    print_header("GitHub Webhook Complete Setup")
    
    # Step 1: Check environment
    print_section("Step 1: Checking Environment")
    
    print("[*] Python version: ", end="")
    success, output = run_command("python --version")
    print(output if success else "ERROR")
    
    print("[*] Git version: ", end="")
    success, output = run_command("git --version")
    print(output if success else "ERROR")
    
    if not os.path.exists('.env.webhook'):
        print("\n[WARNING] .env.webhook not found. Run: python setup_webhook.py")
        return False
    
    print("[OK] .env.webhook found")
    
    # Step 2: Webhook server check
    print_section("Step 2: Verifying Webhook Server")
    
    if not os.path.exists('webhook_server.py'):
        print("[ERROR] webhook_server.py not found!")
        return False
    
    print("[OK] webhook_server.py exists")
    
    # Step 3: Choose deployment mode
    print_section("Step 3: Deployment Mode")
    print("""
1. Local Testing (with ngrok)
   - Run webhook server locally
   - Use ngrok for public URL
   - Good for testing before production

2. Linux Server (Recommended)
   - Deploy to VPS/Linux server
   - Use systemd service
   - Production-ready

3. Windows Server
   - Deploy to Windows server
   - Use Task Scheduler or NSSM
   - Self-hosted option

4. Docker
   - Containerized deployment
   - Works on any platform
   - Cloud-ready
""")
    
    choice = input("Select deployment mode (1-4): ").strip()
    
    deployment_modes = {
        '1': 'local_ngrok',
        '2': 'linux_systemd',
        '3': 'windows_task',
        '4': 'docker'
    }
    
    if choice not in deployment_modes:
        print("[ERROR] Invalid choice!")
        return False
    
    mode = deployment_modes[choice]
    print(f"\n[OK] Selected: {mode}")
    
    # Step 4: GitHub configuration
    print_section("Step 4: GitHub Configuration")
    
    gh_installed, _ = run_command("gh --version")
    
    if gh_installed:
        print("[OK] GitHub CLI found")
        
        auth_ok, _ = run_command("gh auth status")
        if auth_ok:
            print("[OK] GitHub authentication OK")
            use_gh_cli = input("\nUse GitHub CLI to add webhook? (y/n): ").strip().lower()
            if use_gh_cli == 'y':
                print("\n[INFO] Running configure_github_webhook.py...")
                success, _ = run_command("python configure_github_webhook.py")
                if not success:
                    print("[WARNING] GitHub CLI setup failed, continue manual setup")
        else:
            print("[WARNING] GitHub CLI not authenticated")
            print("Run: gh auth login")
    else:
        print("[INFO] GitHub CLI not found")
        print("Install from: https://cli.github.com/")
        print("\nManual GitHub webhook setup:")
        with open('.env.webhook', 'r') as f:
            for line in f:
                if 'GITHUB_WEBHOOK_SECRET=' in line:
                    secret = line.split('=')[1].strip()
                    print(f"\n1. Go to: https://github.com/USERNAME/BRIC/settings/hooks")
                    print(f"2. Click 'Add webhook'")
                    print(f"3. Payload URL: https://your-domain.com/webhook")
                    print(f"4. Secret: {secret}")
                    print(f"5. Content type: application/json")
                    print(f"6. Events: Push events")
                    print(f"7. Click 'Add webhook'")
                    break
    
    # Step 5: Disable GitHub Actions
    print_section("Step 5: Disable GitHub Actions (Optional)")
    
    disable_ga = input("Disable GitHub Actions workflow? (y/n): ").strip().lower()
    
    if disable_ga == 'y':
        print("[INFO] Running disable_github_actions.py...")
        success, output = run_command("python disable_github_actions.py")
        if success:
            print("[OK] GitHub Actions disabled")
        else:
            print(f"[WARNING] Could not disable GitHub Actions: {output}")
    
    # Step 6: Deployment instructions
    print_section("Step 6: Deployment Instructions")
    
    if mode == 'local_ngrok':
        print("""
1. Install ngrok: https://ngrok.com/
2. Start ngrok:
   ngrok http 5000
3. Copy the HTTPS URL (e.g., https://xxxx-xx-xxx-xxx-xx.ngrok.io)
4. Add webhook to GitHub with that URL
5. Start webhook server:
   python webhook_server.py
6. Test by pushing to repository
""")
    
    elif mode == 'linux_systemd':
        print("""
1. On your Linux server, run:
   bash deploy_webhook_linux.sh

2. Configure environment:
   echo 'GITHUB_WEBHOOK_SECRET=your-secret' | sudo tee /etc/environment

3. Reload systemd:
   sudo systemctl daemon-reload
   sudo systemctl restart webhook

4. Check status:
   sudo systemctl status webhook
   sudo journalctl -u webhook -f
""")
    
    elif mode == 'windows_task':
        print("""
1. Using Task Scheduler:
   # Set secret
   $env:GITHUB_WEBHOOK_SECRET = 'your-secret'

   # Create task
   $action = New-ScheduledTaskAction -Execute "python" -Argument "webhook_server.py"
   $trigger = New-ScheduledTaskTrigger -AtStartup
   Register-ScheduledTask -TaskName "GitHub-Webhook" -Action $action -Trigger $trigger -RunLevel Highest

2. Or using NSSM:
   nssm install GitHub-Webhook "python" "webhook_server.py"
   nssm set GitHub-Webhook AppEnvironmentExtra GITHUB_WEBHOOK_SECRET=your-secret
   nssm start GitHub-Webhook

3. Check logs in Event Viewer or:
   nssm query GitHub-Webhook Events
""")
    
    elif mode == 'docker':
        print("""
1. Build Docker image:
   docker build -t github-webhook-server .

2. Run container:
   docker run -d \\
     -p 5000:5000 \\
     -e GITHUB_WEBHOOK_SECRET=your-secret \\
     -v /path/to/repo:/app/repo \\
     github-webhook-server

3. Check logs:
   docker logs -f <container-id>

4. Or use docker-compose:
   See docker-compose.yml for full example
""")
    
    # Summary
    print_header("Setup Complete!")
    
    print("""
Next steps:
1. Add webhook to GitHub (if not done via CLI)
2. Deploy webhook server to your chosen platform
3. Test webhook with a push to your repository
4. Monitor logs for successful updates

For more help:
- WEBHOOK_GUIDE.md - Detailed webhook documentation
- PRODUCTION_DEPLOYMENT.md - Deployment options
- webhook_server.py - Main webhook server code

Questions? Check the troubleshooting section in WEBHOOK_GUIDE.md
""")
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[INFO] Setup cancelled by user")
        exit(1)
    except Exception as e:
        print(f"\n[ERROR] Setup failed: {str(e)}")
        exit(1)
