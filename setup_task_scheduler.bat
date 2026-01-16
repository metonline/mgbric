@echo off
REM Windows Task Scheduler Otomatik Görev Kurulum Script
REM Bu script sistem yöneticisi olarak çalıştırılmalıdır

setlocal enabledelayedexpansion

REM Çalışma dizini
set WORK_DIR=C:\Users\metin\Desktop\BRİÇ
set PYTHON_EXE=%WORK_DIR%\.venv\Scripts\python.exe

echo.
echo ============================================================
echo Windows Task Scheduler - Otomatik Database Güncelleme Kurulumu
echo ============================================================
echo.

REM Kontrol: Python executable var mı?
if not exist "%PYTHON_EXE%" (
    echo [HATA] Python executable bulunamadı: %PYTHON_EXE%
    echo Lütfen .venv klasörü mevcut olduğundan emin ol.
    pause
    exit /b 1
)

echo [1/3] Task Scheduler gorevleri kontrol ediliyor...

REM 1. Seçenek: scheduled_server.py'ı sistem başlangıcında başlat
REM Bu, sunucuyu daima arka planda tutar
schtasks /create /tn "BridgeBot_AutoUpdate" /tr "^"%PYTHON_EXE%^" ^"%WORK_DIR%\scheduled_server.py\"" ^
    /sc onstart /ru SYSTEM /f /rl highest 2>nul

if %ERRORLEVEL% == 0 (
    echo [OK] Görev oluşturuldu: BridgeBot_AutoUpdate (sistem başlangıcında)
) else if %ERRORLEVEL% == 1 (
    echo [HATA] Görev oluşturulamadı. Admin olarak çalıştır!
    pause
    exit /b 1
) else (
    echo [UYARI] Görev zaten var, güncelleniyor...
)

echo [2/3] Görev özellikleri ayarlanıyor...

REM Görevin ayrıntılarını ayarla
schtasks /change /tn "BridgeBot_AutoUpdate" /disable 2>nul
schtasks /change /tn "BridgeBot_AutoUpdate" /enable 2>nul

echo [3/3] Doğrulama yapılıyor...

REM Oluşturduğumuz görevi listele
schtasks /query /tn "BridgeBot_AutoUpdate" /v /fo table 2>nul

echo.
echo ============================================================
echo KURULUM TAMAMLANDI!
echo ============================================================
echo.
echo Görev Bilgileri:
echo   • Adı: BridgeBot_AutoUpdate
echo   • Tetikleyici: Sistem başlangıcında (ve 5 dakikada bir yeniden başlat)
echo   • Çalıştırıcı: scheduled_server.py
echo   • Çalışan: SYSTEM (yönetici yetkisiyle)
echo.
echo Açıklamalar:
echo   • Scheduler her gün 23:59'da otomatik güncelleme tetikler
echo   • http://localhost:5000 - Durum sayfası
echo   • http://localhost:5000/status - Scheduler bilgisi
echo   • Görev yöneticisinde kontrol et: taskmgr.exe
echo.
pause
