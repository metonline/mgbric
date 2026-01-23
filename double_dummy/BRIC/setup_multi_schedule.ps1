# Setup Multiple Scheduled Tasks for BRIC Database Updates
# Triggers Railway webhook at specified times

param(
    [string]$RailwayUrl = "",
    [string]$WebhookSecret = "bric-update-secret-2026",
    [switch]$Remove,
    [switch]$ListTasks
)

$TaskPath = "C:\Users\metin\Desktop\BRIC"

# Schedule times
$ScheduleTimes = @(
    "10:00",
    "12:00",
    "16:00",
    "17:15",
    "17:20",
    "17:25",
    "17:30",
    "17:35",
    "17:40",
    "17:45",
    "17:50",
    "17:55",
    "18:00",
    "23:55"
)

# List existing tasks
if ($ListTasks) {
    Write-Host "`nExisting BRIC Update Tasks:" -ForegroundColor Cyan
    schtasks /query /fo TABLE | Select-String "BRIC"
    exit 0
}

# Remove all BRIC tasks
if ($Remove) {
    Write-Host "Removing all BRIC scheduled tasks..." -ForegroundColor Yellow
    foreach ($Time in $ScheduleTimes) {
        $TaskName = "BRIC_Update_$($Time.Replace(':',''))"
        schtasks /delete /tn $TaskName /f 2>$null
    }
    schtasks /delete /tn "BRIC Database Update" /f 2>$null
    Write-Host "All BRIC tasks removed." -ForegroundColor Green
    exit 0
}

# Create trigger batch file
$BatchPath = Join-Path $TaskPath "trigger_update.bat"
$BatchContent = @"
@echo off
cd /d "$TaskPath"
echo [%date% %time%] BRIC Update Triggered >> update_trigger_log.txt

REM Run local Python update
"$TaskPath\.venv\Scripts\python.exe" "$TaskPath\scheduled_update.py" >> update_trigger_log.txt 2>&1

REM Trigger Railway webhook if configured
if not "$RailwayUrl"=="" (
    curl -X POST "$RailwayUrl/api/webhook/update" -H "X-Webhook-Secret: $WebhookSecret" -H "Content-Type: application/json" -d "{\"type\":\"all\"}" >> update_trigger_log.txt 2>&1
)

echo [%date% %time%] Update Complete >> update_trigger_log.txt
"@

$BatchContent | Out-File -FilePath $BatchPath -Encoding ASCII
Write-Host "Created batch file: $BatchPath" -ForegroundColor Green

# Create scheduled tasks using schtasks
Write-Host "`nCreating scheduled tasks..." -ForegroundColor Cyan
Write-Host "============================================================"

$SuccessCount = 0
foreach ($Time in $ScheduleTimes) {
    $TaskName = "BRIC_Update_$($Time.Replace(':',''))"
    
    # Delete existing task
    schtasks /delete /tn $TaskName /f 2>$null | Out-Null
    
    # Create new task - daily at specified time
    $Result = schtasks /create /tn $TaskName /tr "`"$BatchPath`"" /sc daily /st $Time /f 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] $TaskName ($Time)" -ForegroundColor Green
        $SuccessCount++
    } else {
        Write-Host "  [FAIL] $TaskName - $Result" -ForegroundColor Red
    }
}

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "SCHEDULED TASKS CREATED: $SuccessCount / $($ScheduleTimes.Count)" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green

Write-Host "`nSchedule Summary:" -ForegroundColor Cyan
Write-Host "  - 10:00  (Sabah)"
Write-Host "  - 12:00  (Ogle)"
Write-Host "  - 16:00  (Ogleden sonra)"
Write-Host "  - 17:15 - 18:00 (Her 5 dk turnuva zamani)"
Write-Host "  - 23:55  (Gece - final senkronizasyonu)"

if (-not $RailwayUrl) {
    Write-Host "`n[WARNING] Railway URL not configured!" -ForegroundColor Yellow
    Write-Host "Edit trigger_update.bat to add your Railway URL" -ForegroundColor Yellow
}

Write-Host "`nCommands:" -ForegroundColor Cyan
Write-Host "  List tasks:   .\setup_multi_schedule.ps1 -ListTasks"
Write-Host "  Remove tasks: .\setup_multi_schedule.ps1 -Remove"
Write-Host "  Test run:     .\trigger_update.bat"
