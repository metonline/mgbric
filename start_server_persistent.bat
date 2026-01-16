@echo off
cd /d "%~dp0"
:loop
echo.
echo ==========================================
echo Server basliyor... %date% %time%
echo ==========================================
python http_server.py
echo.
echo !!! Server kapandi, 5 saniye sonra restart...
timeout /t 5
goto loop
pause
