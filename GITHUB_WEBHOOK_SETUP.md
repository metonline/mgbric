# GitHub Webhook Setup Guide

## What is GitHub Webhook?

A webhook automatically triggers actions when you push code to GitHub. Perfect for:
- Auto-deploying your site
- Updating database
- Running tests
- Syncing changes

---

## Step 1: Set Up GitHub Secrets

Your deployment credentials stay secure in GitHub Secrets:

1. Go to: `github.com/metonline/mgbric`
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

Add these secrets:

### Secret 1: DEPLOY_KEY
- **Name**: `DEPLOY_KEY`
- **Value**: Your SSH private key (ask your hosting provider)

### Secret 2: DEPLOY_HOST
- **Name**: `DEPLOY_HOST`
- **Value**: Your server hostname (e.g., `yourserver.com`)

### Secret 3: DEPLOY_USER
- **Name**: `DEPLOY_USER`
- **Value**: SSH username

### Secret 4: DEPLOY_PATH
- **Name**: `DEPLOY_PATH`
- **Value**: Path to your app (e.g., `/home/user/mgbric`)

---

## Step 2: Webhook on Your Server

If using Fly.io, Railway, or Render - **automatic!** (no setup needed)

For **PythonAnywhere**:

1. Ensure `webhook_server.py` is running
2. Go to GitHub repo → Settings → Webhooks
3. Click **Add webhook**
4. **Payload URL**: `https://YOUR_PYTHONANYWHERE_USERNAME.pythonanywhere.com/webhook`
5. **Content type**: `application/json`
6. **Secret**: Set `GITHUB_WEBHOOK_SECRET` environment variable
7. **Events**: Select "Push events"
8. Click **Add webhook**

---

## Step 3: GitHub Actions (Automatic!)

Once set up, **GitHub Actions automatically**:

### On Every Push to `main`:
- ✅ Deploys your code
- ✅ Runs code quality checks
- ✅ Updates staging/production

### Every Day at 2 AM UTC:
- ✅ Updates tournament database
- ✅ Syncs data from Vugraph
- ✅ Commits changes back to GitHub

### On Pull Requests:
- ✅ Runs linting checks
- ✅ Validates Python syntax

---

## Step 4: Check GitHub Actions Status

1. Go to your repo
2. Click **Actions** tab
3. See workflow runs and logs
4. Click on any run to see details

---

## What Workflows Are Running?

### 1. `deploy.yml`
- Triggers: On push to main
- Action: Deploys code to production

### 2. `update-database.yml`
- Triggers: Daily at 2 AM UTC (schedule)
- Action: Updates tournament data, commits back to GitHub

### 3. `lint.yml`
- Triggers: On push, on pull requests
- Action: Checks code quality

---

## Manual Workflow Trigger

You can manually trigger workflows:

1. Go to **Actions** tab
2. Select workflow
3. Click **Run workflow**
4. Watch it execute in real-time

---

## Environment Variables

Set in your GitHub Actions workflow or secrets:

```
FLASK_ENV=production
GITHUB_WEBHOOK_SECRET=your-secret-here
HOSGORU_LANG=tr
```

---

## Troubleshooting

### Workflow Fails to Run
- Check syntax in `.yml` file
- Verify all secrets are set
- Check logs in Actions tab

### Deployment Not Triggering
- Ensure you pushed to `main` branch
- Check webhook configuration
- Verify DEPLOY_KEY is correct

### Database Not Updating
- Check `update-database.yml` is enabled
- Verify cron schedule time
- Check logs for errors

---

## Disable a Workflow

If you want to temporarily disable a workflow:

1. Go to **Actions** tab
2. Click the workflow
3. Click **...** menu
4. Click **Disable workflow**

---

## Next Steps

1. ✅ Add GitHub Secrets (DEPLOY_KEY, DEPLOY_HOST, etc.)
2. ✅ Set up webhook on your server
3. ✅ Push to GitHub and watch Actions run
4. ✅ Monitor logs to confirm everything works

Your site now automatically updates! 🎉
