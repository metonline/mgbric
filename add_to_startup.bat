@echo off
REM Windows Startup klasörüne kısayol ekle

set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set TARGET=C:\Users\metin\Desktop\BRİÇ\scheduled_server.py
set SHORTCUT=%STARTUP_FOLDER%\BridgeBot_Scheduler.lnk
set PYTHON_EXE=C:\Users\metin\Desktop\BRİÇ\.venv\Scripts\python.exe

REM PowerShell ile shortcut oluştur
powershell -Command ^
  "$WshShell = New-Object -ComObject WScript.Shell; " ^
  "$Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); " ^
  "$Shortcut.TargetPath = '%PYTHON_EXE%'; " ^
  "$Shortcut.Arguments = '%TARGET%'; " ^
  "$Shortcut.WorkingDirectory = 'C:\Users\metin\Desktop\BRİÇ'; " ^
  "$Shortcut.Save()"

echo Shortcut oluşturuldu: %SHORTCUT%
timeout /t 3
