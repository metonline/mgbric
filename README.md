# Webhook Server - Shared Hosting Setup

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
