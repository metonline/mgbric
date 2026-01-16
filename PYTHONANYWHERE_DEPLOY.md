# PythonAnywhere Deployment Guide for BRIC

## Quick Deploy (10 minutes)

### Step 1: Sign Up to PythonAnywhere
1. Go to **https://www.pythonanywhere.com**
2. Click **"Pricing & Sign up"**
3. Sign up with GitHub (or email)
4. Choose **Free plan** to start
5. Verify email and complete signup

### Step 2: Create Web App
1. Go to **Web** tab (top menu)
2. Click **"Add a new web app"**
3. Choose **"Clone from existing repo"** or **"Manual configuration"**
4. Select **Python 3.10** (or latest available)

### Step 3: Configure Flask App
1. Go to **Files** tab
2. Upload or clone your repository:
   ```
   git clone https://github.com/metonline/mgbric.git
   ```
3. Or upload your files directly

### Step 4: Set Up WSGI File
Create `wsgi.py` in your project root:
```python
import sys
path = '/home/YOUR_USERNAME/mgbric'
if path not in sys.path:
    sys.path.append(path)

from webhook_server import app

application = app
```

Replace `YOUR_USERNAME` with your PythonAnywhere username.

### Step 5: Configure Web App
1. Go to **Web** tab
2. Find your web app → Click it
3. **Source code**: `/home/YOUR_USERNAME/mgbric`
4. **Working directory**: `/home/YOUR_USERNAME/mgbric`
5. **WSGI configuration file**: `/home/YOUR_USERNAME/mgbric/wsgi.py`
6. **Python version**: 3.10
7. **Virtualenv**: `/home/YOUR_USERNAME/.virtualenvs/mgbric` (or create new)

### Step 6: Install Dependencies
1. Go to **Consoles** tab
2. Click **"Bash console"**
3. Run:
   ```bash
   cd ~/mgbric
   pip install -r requirements.txt
   ```

### Step 7: Reload Web App
1. Go back to **Web** tab
2. Find your app → Click **"Reload"** button
3. Wait 30 seconds for restart

### Step 8: Visit Your Site
Your site will be at: `https://YOUR_USERNAME.pythonanywhere.com`

---

## Features with PythonAnywhere

✅ Python environment pre-configured  
✅ Flask support (perfect for webhook_server.py)  
✅ Free SSL certificate  
✅ Custom domain support (paid tier)  
✅ Scheduled tasks (for automated updates)  
✅ Persistent storage  
✅ Easy to scale  

---

## File Structure for PythonAnywhere

```
mgbric/
├── index.html              # Frontend
├── script.js               # JavaScript
├── style.css               # Styling
├── webhook_server.py       # Flask app
├── wsgi.py                 # WSGI entry point
├── requirements.txt        # Dependencies
├── database.json           # Data (persistent)
└── [other files]           # Assets
```

---

## Environment Variables

In PythonAnywhere Web tab → **Environment variables**:

```
FLASK_ENV=production
GITHUB_WEBHOOK_SECRET=your-secret-here
```

---

## GitHub Webhook Setup

1. Go to GitHub repo → Settings → Webhooks
2. Add webhook:
   - **Payload URL**: `https://YOUR_USERNAME.pythonanywhere.com/webhook`
   - **Content type**: `application/json`
   - **Secret**: Same as `GITHUB_WEBHOOK_SECRET`
   - **Events**: Push events
3. Click **Add webhook**

---

## Troubleshooting

### 502 Bad Gateway
- Check error log in **Web** tab
- Restart web app with **Reload** button
- Ensure `wsgi.py` path is correct

### Module not found
- Run `pip install -r requirements.txt` in bash console
- Make sure virtualenv is activated

### Database file not found
- Check file permissions: `chmod 644 database.json`
- Ensure file is in correct directory

---

## Upgrading Plan

**Free tier** ($0): Perfect to start
- 1 web app
- 512MB storage
- Limited CPU

**Paid tiers** ($5+): For production
- Custom domains
- More storage
- Better performance

---

## Next Steps

1. Sign up at https://www.pythonanywhere.com
2. Create web app with Flask
3. Clone/upload your mgbric repository
4. Install dependencies
5. Configure WSGI file
6. Reload and test!

---

*For detailed PythonAnywhere docs: https://help.pythonanywhere.com*
