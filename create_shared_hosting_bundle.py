#!/usr/bin/env python3
"""
Shared Hosting Deployment Script - FTP Upload Preparation
Creates a webhook bundle ready for shared hosting
"""

import os
import shutil
import zipfile
from datetime import datetime

def create_webhook_bundle():
    """Create a bundle of files for shared hosting deployment"""
    
    print(f"\n{'='*70}")
    print("Webhook Shared Hosting Bundle Creator")
    print(f"{'='*70}\n")
    
    # Files to include
    files_to_include = [
        'webhook_server.py',
        'vugraph_fetcher.py',
        'auto_update_vugraph.py',
        '.env.webhook',
    ]
    
    # Create bundle directory
    bundle_dir = 'webhook_bundle'
    if os.path.exists(bundle_dir):
        shutil.rmtree(bundle_dir)
    os.makedirs(bundle_dir)
    
    print("[1/4] Copying webhook files...")
    
    for file in files_to_include:
        if os.path.exists(file):
            shutil.copy(file, bundle_dir)
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} (not found)")
    
    # Create README with UTF-8 encoding
    print("  ✓ README.md")
    readme_content = """# Webhook Server - Shared Hosting Setup

## Files Included
- webhook_server.py: Main Flask server
- vugraph_fetcher.py: Vugraph data fetcher
- auto_update_vugraph.py: Database update script
- .env.webhook: Webhook secret (KEEP SAFE!)

## Installation Steps

### Option 1: Using cPanel Python App (RECOMMENDED)
1. Upload all files to /home/username/webhook_app/ (via FTP)
2. In cPanel > Software > Setup Python App
3. Select Python version (3.6+)
4. App root: /home/username/webhook_app
5. App domain: mgbric.info
6. App URI: /hosgoru
7. Application startup file: webhook_server.py
8. Click Create
9. Note the public URL assigned

### Option 2: Manual cPanel Setup
1. Upload files via FTP to /public_html/hosgoru/
2. Set permissions: chmod 755 on directories, 644 on files
3. Create .htaccess with proxy rules
4. In cPanel > Cron Jobs > Add job to keep server running

## GitHub Webhook Setup
1. Go to: https://github.com/USERNAME/BRIC/settings/hooks
2. Add webhook with:
   - Payload URL: https://mgbric.info/hosgoru/webhook
   - Secret: (copy from .env.webhook)
   - Events: Push events
   - Active: Yes

## Testing
1. Make a push to your GitHub repository
2. Check GitHub webhook Recent Deliveries
3. Look for Status 200 response
4. Verify database.json updated

## Important
- Keep .env.webhook secure (contains webhook secret)
- Do not commit to GitHub
- Monitor server uptime via cPanel

## Troubleshooting
If webhook does not work:
1. Check cPanel Python app status
2. Review error logs in cPanel
3. Verify .env.webhook has correct secret
4. Test with curl: curl https://mgbric.info/hosgoru/health
"""
    
    with open(os.path.join(bundle_dir, 'README.md'), 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    # Create deployment instructions
    print("  ✓ FTP_UPLOAD_GUIDE.txt")
    instructions = """# FTP Upload Instructions for cPanel Shared Hosting

## Step 1: Download Bundle
1. Download webhook_shared_hosting_[date].zip
2. Extract to a temporary folder

## Step 2: FTP Connection
1. Open FileZilla or any FTP client
2. Connect to mgbric.info:
   - Server: ftp.mgbric.info or your FTP host
   - Username: your cPanel username
   - Password: your cPanel password
   - Port: 21

3. Navigate to home directory (/home/username/)
4. Create new folder: webhook_app
5. Upload all files into webhook_app/

## Step 3: cPanel Configuration
1. Log in to cPanel (cpanel.mgbric.info or control.mgbric.info)
2. Go to Software section > Setup Python App
3. Fill in form:
   - Python version: 3.6 or 3.8+ (any available)
   - Application root: /home/username/webhook_app
   - Application domain: mgbric.info
   - Application URI: /hosgoru
   - Application startup file: webhook_server.py
4. Click "Create" button
5. cPanel shows your Application URL - COPY IT!

## Step 4: Update GitHub Webhook
1. Go to https://github.com/USERNAME/BRIC/settings/hooks
2. Click existing webhook or create new one
3. Update Payload URL to: https://mgbric.info/hosgoru/webhook
4. Content type: application/json
5. Secret: Look in .env.webhook file
6. Save

## Step 5: Test
1. In GitHub webhook settings, click "Recent Deliveries"
2. Make a test push to your repository
3. Check if you see Status 200 response
4. If error, click delivery to see response details

## Troubleshooting

Problem: Status shows error (4xx or 5xx)
Solution:
- Verify .env.webhook has exact secret
- Check Python app is running in cPanel
- Look at error logs in cPanel > Errors section

Problem: Webhook times out
Solution:
- Shared hosting may have execution limits
- Contact hosting provider to increase timeout
- Or use alternative cron method instead

Problem: "Bad address" or connection refused
Solution:
- Check firewall is not blocking
- Verify you're using correct domain (mgbric.info)
- Try test endpoint: https://mgbric.info/hosgoru/health

## Support
If issues persist, contact your hosting provider with:
- Error message from GitHub webhook delivery
- Python app status from cPanel
- Error logs from cPanel
"""
    
    with open(os.path.join(bundle_dir, 'FTP_UPLOAD_GUIDE.txt'), 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    # Create setup checklist
    print("  ✓ SETUP_CHECKLIST.txt")
    checklist = """# Webhook Setup Checklist

Before You Start:
[ ] Have FTP credentials for mgbric.info
[ ] Can access cPanel
[ ] .env.webhook file has webhook secret
[ ] Know your cPanel username

FTP Upload Phase:
[ ] Connect to FTP server
[ ] Create /home/username/webhook_app/ folder
[ ] Upload webhook_server.py
[ ] Upload vugraph_fetcher.py
[ ] Upload auto_update_vugraph.py
[ ] Upload .env.webhook
[ ] Set correct file permissions (755 for .py files)

cPanel Setup Phase:
[ ] Log in to cPanel
[ ] Open Setup Python App
[ ] Python version: 3.6+ selected
[ ] App root path: /home/username/webhook_app
[ ] Domain: mgbric.info
[ ] URI: /hosgoru
[ ] Startup file: webhook_server.py
[ ] Click Create button
[ ] Copy the Application URL shown

GitHub Webhook Phase:
[ ] Go to repository Settings > Webhooks
[ ] Add or update webhook
[ ] Payload URL: https://mgbric.info/hosgoru/webhook
[ ] Secret: (from .env.webhook)
[ ] Content type: application/json
[ ] Events: Push events
[ ] Active: checked
[ ] Save webhook

Testing Phase:
[ ] Make a test push to repository
[ ] Check GitHub Recent Deliveries
[ ] See Status 200 response
[ ] Verify database.json updated
[ ] Check website shows new data

Completed! Webhook is now live.
"""
    
    with open(os.path.join(bundle_dir, 'SETUP_CHECKLIST.txt'), 'w', encoding='utf-8') as f:
        f.write(checklist)
    
    # Create ZIP
    print("\n[2/4] Creating ZIP bundle...")
    
    zip_name = f"webhook_shared_hosting_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.make_archive(zip_name, 'zip', bundle_dir)
    
    print(f"  ✓ Created: {zip_name}.zip")
    
    # Cleanup bundle dir
    print("[3/4] Cleaning up temporary files...")
    shutil.rmtree(bundle_dir)
    print("  ✓ Removed temporary bundle directory")
    
    # Summary
    print(f"\n[4/4] Summary")
    print(f"{'='*70}")
    print(f"""
ZIP File Ready: {zip_name}.zip

What to do next:
1. Download {zip_name}.zip
2. Extract to temporary folder
3. Open FTP_UPLOAD_GUIDE.txt for step-by-step instructions
4. Follow the setup checklist (SETUP_CHECKLIST.txt)

Files included in ZIP:
- webhook_server.py (main server)
- vugraph_fetcher.py (data fetcher)
- auto_update_vugraph.py (update script)
- .env.webhook (webhook secret)
- README.md (detailed setup guide)
- FTP_UPLOAD_GUIDE.txt (FTP & cPanel instructions)
- SETUP_CHECKLIST.txt (step-by-step checklist)

Webhook secret (in .env.webhook):
1440e61bb914225c5e80bb0e5aba7fec

Domain: mgbric.info
Webhook endpoint: https://mgbric.info/hosgoru/webhook

Questions? See README.md in the ZIP file.
{'='*70}
""")
    
    return f"{zip_name}.zip"

if __name__ == '__main__':
    try:
        zip_file = create_webhook_bundle()
        print(f"\n✓ Bundle created successfully!")
        print(f"File: {zip_file}")
        print(f"Size: {os.path.getsize(zip_file) / 1024:.1f} KB")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
