# Windows Task Scheduler - Vugraph Scraper Görevleri Oluştur

$ScriptPath = "C:\Users\metin\Desktop\BRIC\scraper_vugraph.py"
$PythonExe = "C:\Users\metin\Desktop\BRIC\.venv\Scripts\python.exe"
$WorkingDir = "C:\Users\metin\Desktop\BRIC"

# Task 1: 19:00'de Çalış
Write-Host "Task 1: 19:00 görev oluşturuluyor..."
$action1 = New-ScheduledTaskAction -Execute $PythonExe -Argument $ScriptPath -WorkingDirectory $WorkingDir
$trigger1 = New-ScheduledTaskTrigger -Daily -At 19:00
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "VugraphScraper-19" `
    -Action $action1 `
    -Trigger $trigger1 `
    -Principal $principal `
    -Settings $settings `
    -Force

Write-Host "✓ Task 1 oluşturuldu: VugraphScraper-19"

# Task 2: 23:55'te Çalış
Write-Host "Task 2: 23:55 görev oluşturuluyor..."
$action2 = New-ScheduledTaskAction -Execute $PythonExe -Argument $ScriptPath -WorkingDirectory $WorkingDir
$trigger2 = New-ScheduledTaskTrigger -Daily -At 23:55
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "VugraphScraper-2355" `
    -Action $action2 `
    -Trigger $trigger2 `
    -Principal $principal `
    -Settings $settings `
    -Force

Write-Host "✓ Task 2 oluşturuldu: VugraphScraper-2355"

Write-Host "✅ Tüm görevler başarıyla oluşturuldu!"
Write-Host "Kontrol: tasklist /fo list | findstr Vugraph"
