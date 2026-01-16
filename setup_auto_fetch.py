#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Setup automatic scheduled task for tournament data fetching
Runs the auto_fetch_tournaments.py script on a schedule
"""

import subprocess
import sys
import os
from pathlib import Path

def create_windows_scheduled_task():
    """
    Create a Windows Scheduled Task to run auto_fetch_tournaments.py daily
    """
    
    bric_path = Path(__file__).parent.absolute()
    python_exe = Path(sys.executable)
    script_path = bric_path / "auto_fetch_tournaments.py"
    
    # Task name
    task_name = "BRIC_AutoFetchTournaments"
    
    # PowerShell command to create scheduled task
    ps_command = f"""
$TaskName = '{task_name}'
$TaskPath = '\\BRIC\\'
$ScriptPath = '{script_path}'
$PythonExe = '{python_exe}'
$Action = New-ScheduledTaskAction -Execute $PythonExe -Argument $ScriptPath -WorkingDirectory '{bric_path}'
$Trigger = New-ScheduledTaskTrigger -Daily -At 12:00AM
$Settings = New-ScheduledTaskSettingsSet -RunOnlyIfNetworkAvailable -StartWhenAvailable
$Task = New-ScheduledTask -Action $Action -Trigger $Trigger -Settings $Settings -Description 'Automatically fetch new tournament data from Vugraph'

try {{
    Register-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName -InputObject $Task -Force
    Write-Host "✓ Scheduled task created: $TaskName"
    Write-Host "  Runs daily at 12:00 AM"
    Write-Host "  Script: $ScriptPath"
}} catch {{
    Write-Host "✗ Failed to create task: $_"
    exit 1
}}
"""
    
    # Run PowerShell command
    try:
        result = subprocess.run(
            ["powershell", "-Command", ps_command],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"Error: {e}")
        return False


def create_batch_file():
    """
    Create a batch file that can be run from Task Scheduler
    """
    
    bric_path = Path(__file__).parent.absolute()
    batch_file = bric_path / "fetch_tournaments_scheduled.bat"
    
    batch_content = f"""@echo off
REM Automatically fetch tournament data from Vugraph
cd /d "{bric_path}"

REM Activate virtual environment if it exists
if exist ".venv\\Scripts\\activate.bat" (
    call .venv\\Scripts\\activate.bat
)

REM Run the auto fetcher
python auto_fetch_tournaments.py

REM Log the result
echo. >> tournament_fetch.log
echo [%date% %time%] Auto-fetch completed >> tournament_fetch.log
"""
    
    try:
        with open(batch_file, 'w') as f:
            f.write(batch_content)
        
        print(f"✓ Created batch file: {batch_file}")
        print(f"\nTo use with Task Scheduler:")
        print(f"  1. Open Task Scheduler")
        print(f"  2. Create new task")
        print(f"  3. Set Action: {batch_file}")
        print(f"  4. Set Trigger: Daily at desired time")
        
        return True
    except Exception as e:
        print(f"✗ Error creating batch file: {e}")
        return False


def show_options():
    """Display setup options"""
    
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                 AUTOMATIC TOURNAMENT DATA FETCHER SETUP                   ║
╚═══════════════════════════════════════════════════════════════════════════╝

This tool sets up automatic fetching of tournament data from Vugraph.

OPTIONS:
  1. Create Windows Scheduled Task (requires admin)
  2. Create Batch File (for manual scheduling)
  3. Show manual setup instructions
  0. Exit

Choose an option:
""")


def main():
    """Main setup menu"""
    
    print("\n" + "="*75)
    print("AUTOMATIC TOURNAMENT DATA FETCHER - SETUP")
    print("="*75 + "\n")
    
    while True:
        show_options()
        
        try:
            choice = input("Enter choice (0-3): ").strip()
        except KeyboardInterrupt:
            print("\n\nSetup cancelled.")
            return 0
        
        if choice == "1":
            print("\n→ Creating Windows Scheduled Task...")
            if create_windows_scheduled_task():
                print("\n✓ Setup complete!")
                input("Press Enter to continue...")
            else:
                print("\n✗ Setup failed. You may need to run as Administrator.")
                input("Press Enter to continue...")
        
        elif choice == "2":
            print("\n→ Creating Batch File...")
            if create_batch_file():
                print("\n✓ Batch file created!")
                input("Press Enter to continue...")
            else:
                print("\n✗ Failed to create batch file.")
                input("Press Enter to continue...")
        
        elif choice == "3":
            print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                     MANUAL SETUP INSTRUCTIONS                             ║
╚════════════════════════════════════════════════════════════════════════════╝

Option A: Using Windows Task Scheduler

  1. Open Task Scheduler (tasksched.msc)
  2. Create Basic Task
  3. Set Name: "BRIC Auto-Fetch Tournaments"
  4. Set Trigger: Daily at preferred time (e.g., 12:00 AM)
  5. Set Action:
     Program: python.exe
     Arguments: auto_fetch_tournaments.py
     Start in: C:\\Users\\metin\\Desktop\\BRIC
  6. Click Finish

Option B: Using Python Script Directly

  Run from command line:
    python auto_fetch_tournaments.py

  Run with options:
    python auto_fetch_tournaments.py --check    # Check for new dates
    python auto_fetch_tournaments.py --list     # List all dates

Option C: Using Batch File

  Run the batch file created by option 2 above.

""")
            input("Press Enter to continue...")
        
        elif choice == "0":
            print("\nSetup cancelled.")
            return 0
        
        else:
            print("\n✗ Invalid choice. Please try again.")
            input("Press Enter to continue...")


if __name__ == "__main__":
    sys.exit(main())
