#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup automatic data fetching with Windows Task Scheduler
Runs every 6 hours to fetch fresh data and sync to Fly.io
"""

import subprocess
import sys
import os
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TASK_NAME = "BRIC-AutoFetchVugraph"
BATCH_SCRIPT = os.path.join(SCRIPT_DIR, "auto_fetch_and_deploy.bat")
PYTHON_EXE = sys.executable

def create_batch_script():
    """Create batch file for Task Scheduler"""
    batch_content = f"""@echo off
REM Auto-fetch Vugraph data and deploy to Fly.io
cd /d "{SCRIPT_DIR}"

REM Activate virtual environment
call .venv\\Scripts\\activate.bat

REM Fetch data from Vugraph
echo [%date% %time%] Fetching Vugraph data...
python fetch_vugraph_data.py

REM Deploy to Fly.io
echo [%date% %time%] Deploying to Fly.io...
python deploy_to_fly.py

REM Log completion
echo [%date% %time%] Auto-fetch completed >> auto_fetch.log
"""
    
    try:
        with open(BATCH_SCRIPT, 'w', encoding='utf-8') as f:
            f.write(batch_content)
        print(f"✅ Batch script created: {BATCH_SCRIPT}")
        return True
    except Exception as e:
        print(f"❌ Batch script error: {e}")
        return False

def create_scheduled_task():
    """Create Windows Task Scheduler task"""
    
    # PowerShell script to create scheduled task
    ps_script = f"""
$TaskName = "{TASK_NAME}"
$TaskPath = "\\BRIC\\"
$Action = New-ScheduledTaskAction -Execute "{BATCH_SCRIPT}"
$Trigger = @(
    (New-ScheduledTaskTrigger -Daily -At 12:00AM),
    (New-ScheduledTaskTrigger -Daily -At 06:00AM),
    (New-ScheduledTaskTrigger -Daily -At 12:00PM),
    (New-ScheduledTaskTrigger -Daily -At 06:00PM)
)
$Settings = New-ScheduledTaskSettingsSet -RunOnlyIfNetworkAvailable -StartWhenAvailable -MultipleInstances IgnoreNew
$Description = "Automatically fetch tournament data from Vugraph and deploy to Fly.io"

# Remove existing task if present
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath -ErrorAction SilentlyContinue
if ($ExistingTask) {{
    Unregister-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath -Confirm:$false
    Write-Host "Removed existing task"
}}

# Create new task
Register-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description $Description -Force
Write-Host "✓ Task created: $TaskName"
Write-Host "  Run times: 12:00 AM, 06:00 AM, 12:00 PM, 06:00 PM"
"""
    
    try:
        # Write PowerShell script to temp file
        ps_file = os.path.join(SCRIPT_DIR, "create_task_temp.ps1")
        with open(ps_file, 'w', encoding='utf-8') as f:
            f.write(ps_script)
        
        # Execute PowerShell script
        print("🔧 Windows Task Scheduler'da görev oluşturuluyor...")
        result = subprocess.run(
            ['powershell', '-ExecutionPolicy', 'Bypass', '-File', ps_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Clean up temp file
        os.remove(ps_file)
        
        if result.returncode == 0:
            print("✅ Task Scheduler'da görev başarıyla oluşturuldu!")
            print(result.stdout)
            return True
        else:
            print(f"❌ PowerShell hatası:\n{result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Task oluşturma hatası: {e}")
        return False

def verify_task():
    """Verify the scheduled task was created"""
    try:
        print("\n🔍 Görev doğrulanıyor...")
        result = subprocess.run(
            ['powershell', '-Command', f'Get-ScheduledTask -TaskName "{TASK_NAME}" -TaskPath "\\BRIC\\"'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if "BRIC-AutoFetchVugraph" in result.stdout:
            print("✅ Görev başarıyla doğrulandı!")
            return True
        else:
            print("⚠️  Görev doğrulama başarısız")
            return False
    except Exception as e:
        print(f"❌ Doğrulama hatası: {e}")
        return False

if __name__ == '__main__':
    print("="*70)
    print("🤖 OTOMATİK VERI ÇEKME KURULUMU")
    print("="*70 + "\n")
    
    # Step 1: Create batch script
    print("1️⃣  Batch script oluşturuluyor...")
    if not create_batch_script():
        print("\n❌ Kurulum başarısız!")
        sys.exit(1)
    
    # Step 2: Create scheduled task
    print("\n2️⃣  Task Scheduler görev oluşturuluyor...")
    if not create_scheduled_task():
        print("\n❌ Kurulum başarısız!")
        sys.exit(1)
    
    # Step 3: Verify
    print("\n3️⃣  Doğrulama yapılıyor...")
    if verify_task():
        print("\n" + "="*70)
        print("✅ KURULUM BAŞARILI!")
        print("="*70)
        print("\n📅 Çalışma Saatleri:")
        print("   • 00:00 (Gece yarısı)")
        print("   • 06:00 (Sabah)")
        print("   • 12:00 (Öğle)")
        print("   • 18:00 (Akşam)")
        print("\n💡 Log dosyası: auto_fetch.log")
        print("\n🛠️  Görevi durdurmak için:")
        print("   Disable-ScheduledTask -TaskName 'BRIC-AutoFetchVugraph' -TaskPath '\\BRIC\\'")
    else:
        print("\n⚠️  Kurulum tamamlandı ama doğrulama başarısız")
        print("   Görev el ile doğrulayın: Get-ScheduledTask -TaskName 'BRIC-AutoFetchVugraph'")
