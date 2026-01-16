# Database Auto-Sync Setup

## What is Database Auto-Sync?

Automatically updates your tournament data from Vugraph and keeps it synced to GitHub.

Benefits:
- ✅ Data always up-to-date
- ✅ Changes backed up on GitHub
- ✅ Runs on schedule (daily)
- ✅ No manual work needed

---

## How It Works

1. **GitHub Action triggers daily** (2 AM UTC)
2. **Fetches latest tournament data** from Vugraph
3. **Updates `database.json`** locally
4. **Commits changes** to GitHub
5. **Your site automatically loads new data** ✅

---

## Setup Instructions

### Step 1: Enable Auto-Update Workflow

The workflow file is already created: `.github/workflows/update-database.yml`

Just make sure it's committed:
```bash
git add .github/workflows/update-database.yml
git commit -m "Enable auto-update workflow"
git push origin main
```

### Step 2: Configure Schedule (Optional)

Edit `.github/workflows/update-database.yml`:

```yaml
on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM UTC daily
```

Change the time:
- `'0 2 * * *'` = 2 AM UTC every day
- `'0 0 * * 0'` = Midnight UTC every Sunday
- `'0 */6 * * *'` = Every 6 hours

### Step 3: Manual Trigger (Test It)

1. Go to GitHub repo → **Actions** tab
2. Click **Update Database** workflow
3. Click **Run workflow** → **Run workflow**
4. Watch it execute in real-time!

---

## What Gets Updated?

✅ `database.json` - Tournament results
✅ `database.xlsx` - Excel spreadsheet
✅ All player statistics
✅ Hand records
✅ DD values (if available)

---

## Check Update History

Go to GitHub → **Commits** tab

You'll see automatic commits like:
```
Auto-update database from Vugraph - 2026-01-16 02:15:00
```

---

## Disable Auto-Update (If Needed)

In GitHub repo:
1. Go to **Actions** tab
2. Click **Update Database**
3. Click **...** menu
4. Select **Disable workflow**

---

## Database Sync to Your Server

The sync script also automatically pushes to GitHub:

```python
python sync_database_github.py
```

This:
1. Detects changes in database.json
2. Commits with timestamp
3. Pushes to GitHub main branch

---

## GitHub Actions Secrets for Database

If needed, set these in GitHub Secrets:
- `DATABASE_URL` - If using remote database
- `VUGRAPH_API_KEY` - API credentials

---

## Troubleshooting Auto-Update

### Workflow Doesn't Run
- Check GitHub Actions are enabled in repo settings
- Verify `.github/workflows/update-database.yml` exists
- Check for errors in workflow file syntax

### Data Doesn't Update
- Check workflow logs in **Actions** tab
- Ensure Vugraph is accessible
- Verify credentials in `hosgoru.py`

### Commit Not Appearing
- Check workflow logs for `git push` errors
- Verify GitHub token has write access
- Check branch is `main`

---

## Advanced: Custom Update Script

Create your own update script:

```bash
#!/bin/bash
cd ~/mgbric
python run_bot.py --lang tr --retries 3
git add database.json
git commit -m "Manual database update"
git push origin main
```

Run manually whenever needed!

---

## Monitoring Updates

### Via GitHub
1. Go to **Commits** tab
2. See all auto-updates with timestamps
3. Click to see what changed

### Via Logs
In **Actions** tab:
1. Click **Update Database** workflow
2. Select latest run
3. View detailed logs

---

## Next Steps

1. ✅ Ensure `.github/workflows/update-database.yml` is committed
2. ✅ Go to **Actions** tab and test manually
3. ✅ Wait for scheduled run (2 AM UTC next day)
4. ✅ Check GitHub commits for auto-updates
5. ✅ Verify your site loads updated data ✅

Your database now auto-updates! 🎉
