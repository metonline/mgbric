# Windows Scheduled Task olarak Flask sunucusunu ayarla
# Bu script yönetici olarak çalıştırılmalı

$TaskName = "BridgeFlaskServer"
$ScriptPath = "C:\Users\metin\Desktop\BRİÇ\scheduled_server.py"
$WorkDir = "C:\Users\metin\Desktop\BRİÇ"
$PythonExe = "python"

# Eğer task varsa sil
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Eski task silindi"
}

# Yeni task oluştur
$action = New-ScheduledTaskAction -Execute $PythonExe -Argument $ScriptPath -WorkingDirectory $WorkDir
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -RunLevel Highest
$settings = New-ScheduledTaskSettingSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "Flask Bridge Tournament Server - Auto Start"

Write-Host "✓ Task oluşturuldu: $TaskName"
Write-Host "✓ Sunucu her açılışta otomatik başlayacak (http://localhost:5000)"
