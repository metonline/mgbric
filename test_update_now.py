import ftplib
import subprocess
import os

FTP_HOST = 'ftp.mgbric.info'
FTP_USER = 'mgb3dcinfo'
FTP_PASS = '34b2e-c68c17'
FTP_PATH = '/public_html/hosgoru/'

# Download and run the script locally to test
try:
    ftp = ftplib.FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    ftp.cwd(FTP_PATH)
    
    print("📥 Downloading auto_update_vugraph.py...")
    with open('temp_auto_update.py', 'wb') as f:
        ftp.retrbinary('RETR auto_update_vugraph.py', f.write)
    
    ftp.quit()
    
    print("▶️ Running update script...\n")
    result = subprocess.run(['python', 'temp_auto_update.py'], 
                          capture_output=True, text=True, timeout=60)
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    os.remove('temp_auto_update.py')
    
except Exception as e:
    print(f"❌ Error: {e}")
