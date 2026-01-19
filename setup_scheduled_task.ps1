# Setup Scheduled Task for BRIC Database Updates
# Run this script as Administrator to create the scheduled task

param(
    [string]$TaskName = "BRIC Database Update",
    [string]$TriggerTime = "23:00",
    [switch]$Remove
)

$TaskPath = "C:\Users\metin\Desktop\BRIC"
$BatchFile = Join-Path $TaskPath "run_scheduled_update.bat"

# Remove existing task if requested
if ($Remove) {
    Write-Host "Removing scheduled task '$TaskName'..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Task removed successfully." -ForegroundColor Green
    exit 0
}

# Check if batch file exists
if (-not (Test-Path $BatchFile)) {
    Write-Host "Error: Batch file not found at $BatchFile" -ForegroundColor Red
    exit 1
}

Write-Host "Setting up scheduled task for BRIC Database Update..." -ForegroundColor Cyan
Write-Host ""

# Create the action
$Action = New-ScheduledTaskAction -Execute $BatchFile -WorkingDirectory $TaskPath

# Create the trigger (daily at specified time)
$Trigger = New-ScheduledTaskTrigger -Daily -At $TriggerTime

# Create the settings
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

# Create the principal (run whether user is logged on or not)
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

# Remove existing task if exists
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($ExistingTask) {
    Write-Host "Removing existing task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Create the task
try {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description "Automatically fetches new tournament data from Vugraph and updates the BRIC database daily"
    
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Green
    Write-Host "Scheduled task created successfully!" -ForegroundColor Green
    Write-Host "=" * 60 -ForegroundColor Green
    Write-Host ""
    Write-Host "Task Name: $TaskName"
    Write-Host "Trigger: Daily at $TriggerTime"
    Write-Host "Action: $BatchFile"
    Write-Host ""
    Write-Host "The database will be automatically updated every day at $TriggerTime."
    Write-Host ""
    Write-Host "To manually run the task:"
    Write-Host "  Start-ScheduledTask -TaskName '$TaskName'"
    Write-Host ""
    Write-Host "To remove the task:"
    Write-Host "  .\setup_scheduled_task.ps1 -Remove"
    Write-Host ""
    
} catch {
    Write-Host "Error creating scheduled task: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "You may need to run this script as Administrator." -ForegroundColor Yellow
    exit 1
}
