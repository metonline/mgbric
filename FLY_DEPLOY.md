# Deploy BRIC to Fly.io

## Quick Deploy (5 minutes)

### Step 1: Install Fly CLI
Download from: https://fly.io/docs/getting-started/installing-flyctl/

Or with PowerShell:
```powershell
choco install flyctl
# or
iex "& { $(irm https://fly.io/install.ps1) }"
```

### Step 2: Sign Up to Fly.io
```bash
flyctl auth signup
# or
flyctl auth login
```

### Step 3: Launch Your App
From your BRIC directory:
```bash
cd C:\Users\metin\Desktop\BRIC
flyctl launch
```

When prompted:
- **App name**: `bric-tournament` (or your choice)
- **Region**: Choose closest to you (or `ams` for Europe/Turkey)
- **Postgres database**: No
- **Deploy now**: Yes

### Step 4: Wait for Deployment
Watch the logs in real-time. When complete, you'll see:
```
Visit your newly deployed app at https://bric-tournament.fly.dev
```

### Step 5: Done! 🎉
Your app is live at: `https://bric-tournament.fly.dev`

---

## Files Included

- **Dockerfile** - Container configuration
- **fly.toml** - Fly.io settings
- **.dockerignore** - Files to exclude from Docker

---

## Environment Variables (Optional)

Set GitHub webhook secret:
```bash
flyctl secrets set GITHUB_WEBHOOK_SECRET=your-secret-here
```

---

## Scale Your App (Later)

Add more machines:
```bash
flyctl scale count 2
```

Increase memory:
```bash
flyctl scale memory 1024
```

---

## View Logs

```bash
flyctl logs
```

---

## Monitoring

View app status:
```bash
flyctl status
```

---

## Useful Commands

| Command | Action |
|---------|--------|
| `flyctl deploy` | Redeploy from current code |
| `flyctl logs` | View live logs |
| `flyctl status` | Show app status |
| `flyctl destroy` | Delete app |
| `flyctl scale count 2` | Run 2 instances |

---

## Troubleshooting

### App won't start
```bash
flyctl logs
# Check for errors in the logs
```

### Port issues
Fly.io automatically maps port 8080 (defined in Dockerfile)

### Database not persisting
Files are stored in `/app/data` volume (1GB free)

---

## Next Steps

1. Install Fly CLI
2. Run `flyctl launch` from your BRIC directory
3. Deploy!
4. Visit your live URL

---

Visit: https://fly.io/docs for full documentation
