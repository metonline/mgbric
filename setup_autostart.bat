@echo off
REM Windows Scheduled Task oluştur - Flask sunucusunu otomatik başlat
REM Yönetici olarak çalıştırılmalı!

setlocal enabledelayedexpansion

set TASK_NAME=BridgeFlaskServer
set PYTHON_EXE=python.exe
set SCRIPT_PATH=C:\Users\metin\Desktop\BRİÇ\scheduled_server.py
set WORK_DIR=C:\Users\metin\Desktop\BRİÇ

REM Eski task'i sil (varsa)
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "python.exe" >NUL
if "%ERRORLEVEL%"=="0" (
    echo Flask sunucusu zaten çalışıyor, devam edilmeden önce kapanmalı...
    echo Lütfen sunucuyu kapatın ve tekrar deneyin.
    timeout /t 3 /nobreak
    exit /b 1
)

REM Task oluştur
schtasks /CREATE /TN "%TASK_NAME%" /TR "\"%PYTHON_EXE%\" \"%SCRIPT_PATH%\"" /SC ONSTART /RU %USERNAME% /F

if "%ERRORLEVEL%"=="0" (
    echo.
    echo ✓ Görev başarıyla oluşturuldu!
    echo ✓ Task adı: %TASK_NAME%
    echo ✓ Sunucu her açılışta otomatik başlayacak
    echo ✓ Erişim: http://localhost:5000
    echo.
) else (
    echo ✗ Görev oluşturma başarısız oldu.
    echo Yönetici olarak çalıştırdığınızdan emin olun.
)

pause
