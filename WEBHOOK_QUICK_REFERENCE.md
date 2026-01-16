# Webhook Quick Reference Card

## 🔑 Essential Info

**Webhook Secret**: `1440e61bb914225c5e80bb0e5aba7fec`

**GitHub Hook URL**: `https://github.com/USERNAME/BRIC/settings/hooks`

**Webhook Payload URL**: `https://your-domain.com/webhook`

---

## ⚡ One-Liner Commands

### Start Webhook Locally
```powershell
$env:GITHUB_WEBHOOK_SECRET = '1440e61bb914225c5e80bb0e5aba7fec'; python webhook_server.py
```

### Test Webhook
```bash
$env:GITHUB_WEBHOOK_SECRET = '1440e61bb914225c5e80bb0e5aba7fec'; python test_webhook.py
```

### Check Health
```bash
curl http://localhost:5000/health
```

### Deploy to Linux
```bash
bash deploy_webhook_linux.sh
```

### Deploy with Docker
```bash
docker-compose up -d
```

---

## 📝 GitHub Webhook Settings (Copy-Paste)

**Payload URL**: 
```
https://your-domain.com/webhook
```

**Secret**: 
```
1440e61bb914225c5e80bb0e5aba7fec
```

**Content Type**: 
```
application/json
```

**Which events**: 
```
✓ Push events
```

**Active**: 
```
✓ Checked
```

---

## 🔍 Common Commands

```bash
# Windows - Set secret and start server
$env:GITHUB_WEBHOOK_SECRET = '1440e61bb914225c5e80bb0e5aba7fec'
python webhook_server.py

# Linux - Check webhook service
sudo systemctl status webhook
sudo journalctl -u webhook -f

# Docker - View logs
docker logs -f github-webhook

# Check if port is open
netstat -ano | findstr :5000

# Test health endpoint
curl http://localhost:5000/health
curl http://127.0.0.1:5000/status
```

---

## 📋 Setup Checklist (Copy-Paste)

```
[ ] Generated webhook secret
[ ] Created .env.webhook file
[ ] Tested webhook_server.py locally
[ ] Tested test_webhook.py
[ ] Added webhook to GitHub
[ ] Disabled GitHub Actions workflow
[ ] Deployed server to production
[ ] Verified firewall rules
[ ] Set up monitoring
[ ] Tested end-to-end (push → update)
[ ] Backed up webhook secret
```

---

## 🚀 3-Step Deployment

**Step 1: GitHub Setup** (2 min)
```
1. https://github.com/USERNAME/BRIC/settings/hooks
2. Add webhook
3. Use values from GitHub Webhook Settings above
```

**Step 2: Server Deploy** (5 min)
```
Choice 1 - Local: python webhook_server.py
Choice 2 - Linux: bash deploy_webhook_linux.sh
Choice 3 - Docker: docker-compose up -d
```

**Step 3: Test** (1 min)
```
1. python test_webhook.py
2. Push to GitHub
3. Check logs
```

---

## 📊 File Overview

| File | Purpose | Run With |
|------|---------|----------|
| `webhook_server.py` | Main server | `python` |
| `setup_webhook.py` | Setup wizard | `python` |
| `test_webhook.py` | Test tool | `python` |
| `deploy_webhook_linux.sh` | Linux deploy | `bash` |
| `docker-compose.yml` | Docker deploy | `docker-compose` |

---

## 🔗 Links

- **GitHub Webhook Settings**: https://github.com/USERNAME/BRIC/settings/hooks
- **Full Guide**: See `WEBHOOK_GUIDE.md`
- **Deployment Options**: See `PRODUCTION_DEPLOYMENT.md`
- **Complete Setup**: See `WEBHOOK_COMPLETE_SETUP.md`

---

## ⚠️ Important Notes

- ✅ GitHub Actions is DISABLED (workflow commented)
- ✅ Webhook server is READY
- ✅ Secret is GENERATED
- ⚠️ Keep secret SECRET (never commit)
- ⚠️ Use HTTPS in production
- ⚠️ Test before production deploy

---

## 🆘 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 5000 in use | `netstat -ano \| findstr :5000` |
| Signature mismatch | Verify secret matches |
| No updates | Check logs in webhook_server |
| Push failed | Check git credentials |
| HTTPS error | Check SSL certificate |

---

**Print this card and keep it handy!** 📌

---

Generated: 2026-01-02
Version: 1.0
Status: ✅ READY
