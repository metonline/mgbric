# Render Deployment Guide for BRIC

## Quick Start - Deploy in 5 Minutes

### Option 1: Static Site Only (Fastest)
1. Go to [render.com](https://render.com)
2. Click "New +" → "Static Site"
3. Connect your GitHub repo
4. Set **Build Command**: `echo "Ready"` (or leave blank)
5. Set **Publish Directory**: `.` (current directory)
6. Deploy!

### Option 2: Full Stack (Static + Flask Backend)
1. Go to [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repo
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -w 4 -b 0.0.0.0:$PORT webhook_server:app`
   - **Environment**: Add `GITHUB_WEBHOOK_SECRET` from your GitHub webhook settings
5. Deploy!

## Files Prepared for Render

- ✅ `requirements.txt` - Python dependencies
- ✅ `render.yaml` - Deployment configuration
- ✅ `Procfile` - Process file for web service
- ✅ `.gitignore` - Already configured

## Important Notes

### Database Persistence
Since Render's free tier uses ephemeral storage:
- Store `database.json` on GitHub (commit and push)
- Use GitHub Actions for automated updates
- Or upgrade to Render paid tier for persistent disk

### GitHub Webhook Integration
If using the Flask backend:
1. Go to GitHub repo → Settings → Webhooks
2. Payload URL: `https://your-render-url/webhook`
3. Content type: `application/json`
4. Secret: Set `GITHUB_WEBHOOK_SECRET` environment variable
5. Events: Select "Push events"

### Custom Domain
1. After deployment, go to Render dashboard
2. Your service → Settings → Custom Domain
3. Add your domain name

## Environment Variables Needed

If deploying Flask backend, set in Render dashboard:
```
GITHUB_WEBHOOK_SECRET=your-secret-here
FLASK_ENV=production
```

## File Structure for Render
```
BRIC/
├── index.html              # Main frontend
├── script.js               # Frontend logic
├── style.css               # Styling
├── webhook_server.py       # Flask backend (if using)
├── requirements.txt        # Python dependencies
├── render.yaml             # Render config
├── Procfile                # Process definition
├── .gitignore              # Git ignore rules
└── database.json           # Tournament data (optional)
```

## Troubleshooting

### Deploy fails on "gunicorn not found"
- Ensure `gunicorn` is in `requirements.txt`
- Check: `pip freeze | grep gunicorn`

### Webhook not triggering
- Verify webhook URL is correct in GitHub
- Check Render logs: `render logs` command
- Ensure `GITHUB_WEBHOOK_SECRET` is set

### Database not persisting
- Use `git` to commit changes to `database.json`
- Push to GitHub before redeployment
- Render pulls from GitHub on each build

## Next Steps

1. **Push to GitHub**
   ```bash
   git add requirements.txt render.yaml Procfile RENDER_DEPLOY.md
   git commit -m "Add Render deployment files"
   git push origin main
   ```

2. **Connect Render Account**
   - Sign up at [render.com](https://render.com)
   - Connect your GitHub account

3. **Create New Service**
   - Choose Static Site (Option 1) or Web Service (Option 2)
   - Select your BRIC repository
   - Follow the configuration above

4. **Monitor Deployment**
   - Watch logs in Render dashboard
   - Test the deployment URL

## Support

- Render Docs: https://render.com/docs
- Flask Guide: https://flask.palletsprojects.com/
- Environment Variables: https://render.com/docs/environment-variables

---
Generated for: BRIC Tournament Analysis Application
Date: January 2026
