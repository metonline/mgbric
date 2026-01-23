@echo off
cd /d "C:\Users\metin\Desktop\BRIC"
echo [%date% %time%] BRIC Update Triggered >> update_trigger_log.txt

REM ============================================
REM Railway URL
SET RAILWAY_URL=https://mgbric.up.railway.app
REM ============================================

SET WEBHOOK_SECRET=bric-update-secret-2026

REM Run local Python update
echo [%date% %time%] Running local update... >> update_trigger_log.txt
"C:\Users\metin\Desktop\BRIC\.venv\Scripts\python.exe" "C:\Users\metin\Desktop\BRIC\scheduled_update.py" >> update_trigger_log.txt 2>&1

REM Trigger Railway webhook if configured
if not "%RAILWAY_URL%"=="" (
    echo [%date% %time%] Triggering Railway webhook: %RAILWAY_URL% >> update_trigger_log.txt
    curl -s -X POST "%RAILWAY_URL%/api/webhook/update" -H "X-Webhook-Secret: %WEBHOOK_SECRET%" -H "Content-Type: application/json" -d "{\"type\":\"all\"}" >> update_trigger_log.txt 2>&1
) else (
    echo [%date% %time%] Railway URL not configured, skipping webhook >> update_trigger_log.txt
)

echo [%date% %time%] Update Complete >> update_trigger_log.txt
echo. >> update_trigger_log.txt
