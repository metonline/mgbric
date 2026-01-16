# ✅ BRIC on Render - Complete Setup Guide

## What's Been Done ✓

I've created all necessary files for deploying your BRIC tournament analysis platform to Render:

### Created Files:
1. **`requirements.txt`** - All Python dependencies
2. **`Procfile`** - How to start the Flask server on Render
3. **`render.yaml`** - Render service configuration
4. **`build.sh`** - Build script for preparation
5. **`RENDER_DEPLOY.md`** - Detailed deployment guide
6. **`prepare_render_deploy.py`** - Pre-deployment checker

---

## 🚀 Quick Deploy (Choose One)

### Option A: Static Site Only (⚡ Fastest - 2 minutes)
Perfect if you just want the web interface without the webhook backend.

```bash
# 1. Commit files
git add requirements.txt Procfile RENDER_DEPLOY.md render.yaml build.sh prepare_render_deploy.py
git commit -m "Add Render deployment files"
git push origin main

# 2. Go to https://render.com → New → Static Site
# 3. Connect GitHub repo (BRIC)
# 4. Settings:
#    - Name: bric-tournament-analysis
#    - Branch: main
#    - Build Command: echo "Building..."
#    - Publish Directory: .
# 5. Click Deploy
```

### Option B: Full Stack with Backend (🔧 Complete - 5 minutes)
Includes Flask webhook server for GitHub integration and automatic updates.

```bash
# 1. Commit files
git add requirements.txt Procfile RENDER_DEPLOY.md render.yaml build.sh prepare_render_deploy.py
git commit -m "Add Render deployment files"
git push origin main

# 2. Go to https://render.com → New → Web Service
# 3. Connect GitHub repo (BRIC)
# 4. Settings:
#    - Name: bric-tournament-api
#    - Environment: Python 3
#    - Build Command: pip install -r requirements.txt
#    - Start Command: gunicorn -w 4 -b 0.0.0.0:$PORT webhook_server:app
#    - Instance Type: Free
# 5. Environment Variables:
#    - GITHUB_WEBHOOK_SECRET: (from GitHub webhook settings)
#    - FLASK_ENV: production
# 6. Click Deploy
```

---

## 📋 Pre-Deployment Checklist

- [ ] All files created (see Created Files above)
- [ ] Git repository is initialized: `git status`
- [ ] Git is configured: `git config --global user.name` and `user.email`
- [ ] You have a Render account: https://render.com/signup
- [ ] Your GitHub account is connected to Render
- [ ] (Optional) GitHub Personal Access Token for webhook if needed

---

## 🔗 Step-by-Step Deployment

### Step 1: Verify Everything is Ready
```bash
python prepare_render_deploy.py
```
This checks:
- ✓ Git repository
- ✓ All deployment files
- ✓ Git configuration

### Step 2: Push to GitHub
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### Step 3: Sign Up to Render
- Go to https://render.com
- Sign up with GitHub (recommended)
- Connect your GitHub account

### Step 4: Create New Service
**Choose your deployment type:**

#### For Static Site:
1. Dashboard → New (+) → Static Site
2. Select BRIC repository
3. Auto-fill: 
   - **Build Command**: Leave blank or `echo "Build complete"`
   - **Publish Directory**: `.`
4. Create Static Site

#### For Web Service (with backend):
1. Dashboard → New (+) → Web Service
2. Select BRIC repository
3. Fill in:
   - **Name**: `bric-tournament-api`
   - **Environment**: Python 3
   - **Region**: nearest to you
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -w 4 -b 0.0.0.0:$PORT webhook_server:app`
   - **Instance Type**: Free
4. Click "Advanced" and add Environment Variables:
   - `GITHUB_WEBHOOK_SECRET`: Get from GitHub repo → Settings → Webhooks
   - `FLASK_ENV`: `production`
5. Click "Create Web Service"

### Step 5: Wait for Deployment
- Render will automatically:
  - Pull your code from GitHub
  - Install dependencies
  - Start the application
  - Give you a URL (e.g., `https://bric-tournament-api.onrender.com`)

### Step 6: Test Your Site
- Click the URL from Render dashboard
- Test the interface loads
- Verify functionality works

---

## 📱 URL After Deployment

After deployment, Render gives you:
- **Static Site**: `https://bric-tournament-analysis.onrender.com/`
- **Web Service**: `https://bric-tournament-api.onrender.com/`

Access the full URL and bookmark it!

---

## 🔐 GitHub Webhook Setup (Optional)

If using Web Service backend:

1. Go to your GitHub repository
2. Settings → Webhooks → Add webhook
3. Configure:
   - **Payload URL**: `https://YOUR-RENDER-URL/webhook`
   - **Content type**: `application/json`
   - **Secret**: Same as `GITHUB_WEBHOOK_SECRET` in Render
   - **Events**: Select "Push events"
4. Click "Add webhook"
5. Render will now automatically update when you push code

---

## 💾 Database Persistence

⚠️ **Important**: Render's free tier has ephemeral storage.

### Solution: Store on GitHub
```bash
# After updating database locally:
git add database.json
git commit -m "Update tournament database"
git push origin main
```

Render will pull latest on each deployment.

### Better Solution: Use Render Disk
- Upgrade to Render Starter ($7/month)
- Get persistent disk storage
- Add to `render.yaml`:
  ```yaml
  disk:
    name: bric-data
    mountPath: /data
    sizeGb: 10
  ```

---

## 🎯 What Files Go Where?

Render will serve these automatically:

```
BRIC/
├── index.html          → Home page (/)
├── script.js           → JavaScript logic
├── style.css           → Styles
├── database.json       → Tournament data
├── webhook_server.py   → Backend API (if Web Service)
├── requirements.txt    → Dependencies
├── Procfile            → Startup command
└── [other files]       → Static assets
```

---

## ⚙️ Configuration Explained

### `requirements.txt`
Lists all Python packages needed:
- `flask` - Web framework
- `gunicorn` - Production server
- `pandas` - Data processing
- `beautifulsoup4` - Web scraping
- `requests` - HTTP client

### `Procfile`
Tells Render how to start your app:
```
web: gunicorn -w 4 -b 0.0.0.0:$PORT webhook_server:app
```

### `render.yaml`
(Alternative to manual setup) Define services in code.

---

## 🆘 Troubleshooting

### "Build failed - missing dependencies"
✓ Fixed: `requirements.txt` has all needed packages

### "404 Not Found"
- Check publish directory is `.` (root)
- Files must be in repository root, not in subfolder

### "Webhook not triggering"
- Verify webhook URL is correct in GitHub
- Check `GITHUB_WEBHOOK_SECRET` matches
- View Render logs: Render dashboard → Logs

### "Database not updating"
- Commit changes to Git first: `git add database.json && git commit && git push`
- Render pulls from GitHub on each build

### "Takes too long to start"
- Reduce workers in Procfile: `-w 2` instead of `-w 4`
- Upgrade instance type if needed

---

## 📊 Estimated Deployment Time

| Step | Time |
|------|------|
| Commit & push | 1 min |
| Render build | 2-3 min |
| First deploy | 1 min |
| **Total** | **5 min** |

---

## 🎓 Next Steps

### After Initial Deploy:
1. ✅ Test the live URL
2. ✅ Configure custom domain (if you have one)
3. ✅ Set up GitHub webhook (if using backend)
4. ✅ Enable auto-deploys on GitHub push

### Advanced (Optional):
- Add monitoring/alerts
- Set up backup strategy
- Configure CDN for faster loading
- Add API rate limiting

---

## 📞 Support Resources

- **Render Docs**: https://render.com/docs
- **Flask Docs**: https://flask.palletsprojects.com/
- **Gunicorn Docs**: https://gunicorn.org/
- **GitHub Webhooks**: https://docs.github.com/en/developers/webhooks-and-events/webhooks

---

## ✨ Summary

Your BRIC tournament analysis platform is now ready for cloud deployment! 

**Next Action**: Run `prepare_render_deploy.py` to verify everything, then push to GitHub and deploy on Render.

```bash
python prepare_render_deploy.py
```

Good luck! 🚀

---

*Generated: January 2026 | For: BRIC Tournament Analysis Platform*
