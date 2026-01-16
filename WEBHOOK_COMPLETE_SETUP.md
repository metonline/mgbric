# GitHub Webhook Server - Complete Setup Guide

## Hızlı Başlangıç

```powershell
# 1. Webhook secret oluştur
python setup_webhook.py

# 2. Master setup'ı çalıştır
python master_webhook_setup.py

# 3. Talimatları takip et
```

## Tüm Dosyalar

| Dosya | Amaç |
|-------|------|
| `webhook_server.py` | Ana webhook sunucusu |
| `setup_webhook.py` | Secret oluşturma wizard'ı |
| `test_webhook.py` | Webhook test aracı |
| `master_webhook_setup.py` | Tüm kurulumu otomatize et |
| `configure_github_webhook.py` | GitHub CLI ile webhook ekle |
| `disable_github_actions.py` | GitHub Actions'ı devre dışı bırak |
| `WEBHOOK_GUIDE.md` | Detaylı dokümantasyon |
| `PRODUCTION_DEPLOYMENT.md` | Deployment seçenekleri |
| `docker-compose.yml` | Docker deployment |
| `nginx.conf` | Nginx reverse proxy config |

## Deployment Seçenekleri

### 1. Local Testing with ngrok

```bash
# ngrok'u kur
# https://ngrok.com/ adresinden indir

# ngrok başlat
ngrok http 5000

# Webhook server başlat (yeni terminal)
python webhook_server.py

# GitHub webhook URL'sini güncelle
# https://xxx-xx-xxx-xxx-xx.ngrok.io/webhook
```

### 2. Linux/Ubuntu Server (Recommended)

```bash
# VPS'te çalıştır
bash deploy_webhook_linux.sh

# Kontrol et
sudo systemctl status webhook
sudo journalctl -u webhook -f
```

### 3. Windows Server

**Option A: Task Scheduler**
```powershell
$action = New-ScheduledTaskAction -Execute "python" -Argument "webhook_server.py"
$trigger = New-ScheduledTaskTrigger -AtStartup
Register-ScheduledTask -TaskName "GitHub-Webhook" -Action $action -Trigger $trigger -RunLevel Highest
```

**Option B: NSSM**
```powershell
nssm install GitHub-Webhook python webhook_server.py
nssm start GitHub-Webhook
```

### 4. Docker (Cloud-Ready)

```bash
# Image oluştur
docker build -t github-webhook-server .

# Çalıştır
docker-compose up -d

# Logları kontrol et
docker logs -f github-webhook
```

## GitHub Webhook Setup

### Option 1: GitHub CLI (Otomatik)

```bash
python configure_github_webhook.py
```

### Option 2: Manual

1. `https://github.com/USERNAME/BRIC/settings/hooks`
2. "Add webhook" tıkla
3. Ayarlar:
   - **Payload URL**: `https://your-domain.com/webhook`
   - **Content type**: `application/json`
   - **Secret**: `.env.webhook` dosyasından al
   - **Events**: `Push events`
4. "Add webhook" tıkla

## GitHub Actions'ı Devre Dışı Bırak

GitHub Actions'ı webhook'a geçince devre dışı bırak (duplicate updates için):

```bash
python disable_github_actions.py
```

Veya manual olarak `.github/workflows/update-from-vugraph.yml` dosyasını kapat.

## Test Etme

### Health Check
```bash
curl http://localhost:5000/health
```

### Status
```bash
curl http://localhost:5000/status
```

### Webhook Test
```bash
python test_webhook.py
```

## Troubleshooting

### Port 5000 Conflict
```bash
# Port'u değiştir webhook_server.py'de:
# app.run(host='0.0.0.0', port=5001, debug=False)
```

### Webhook Secret Hatası
```bash
# Secret'ı kontrol et
cat .env.webhook

# Ortam değişkenini kontrol et
echo $env:GITHUB_WEBHOOK_SECRET
```

### Connection Refused
```bash
# Server çalışıyor mu?
netstat -ano | findstr :5000

# Firewall'u kontrol et
netsh advfirewall firewall show rule name="Python"
```

### Git Push Hatası
```bash
# Git credentials'ı kontrol et
git config user.email
git config user.name

# SSH key'i kontrol et
ssh -T git@github.com
```

## Monitoring

### Linux
```bash
# Real-time logs
sudo journalctl -u webhook.service -f

# Service status
sudo systemctl status webhook.service

# Restart service
sudo systemctl restart webhook.service
```

### Windows
```powershell
# Task görüntüle
Get-ScheduledTask -TaskName "GitHub-Webhook"

# Event logs
Get-EventLog -LogName System | Where {$_.Source -eq "Task Scheduler"}

# NSSM logs
nssm query GitHub-Webhook Events
```

### Docker
```bash
# Container logs
docker logs -f github-webhook

# Container status
docker ps | grep webhook

# Container restart
docker restart github-webhook
```

## Security

⚠️ **ÖNEMLI**:
1. Webhook secret'ını asla GitHub'da yayınlamayın
2. `.env.webhook` dosyasını `.gitignore`'a ekleyin
3. Production'da HTTPS kullanın
4. Firewall'da sadece gerekli portları açın
5. Regular olarak logs'ları kontrol edin

## Performance

- Flask development server'ı production için yeterli değildir
- Production'da Gunicorn/uWSGI kullanın:
  ```bash
  pip install gunicorn
  gunicorn -w 4 -b 0.0.0.0:5000 webhook_server:app
  ```

## Logs

Webhook işlemleri console ve dosyalarda kaydedilir:

```
[2026-01-02 10:30:15] GitHub Webhook Received!
[2026-01-02 10:30:15] Step 1: Pull latest files from GitHub
[2026-01-02 10:30:16] Git pull successful
[2026-01-02 10:30:16] Step 2: Update database from Vugraph
[2026-01-02 10:30:25] Database updated successfully
[2026-01-02 10:30:26] Step 3: Commit and push changes
[2026-01-02 10:30:28] Changes pushed to GitHub
[2026-01-02 10:30:28] Webhook processing completed!
```

## Architecture

```
GitHub (push event)
    ↓
Webhook Server (Flask)
    ↓
┌──────────────────────┐
│ 1. Git Pull (main)   │
│ 2. Vugraph Update    │
│ 3. Database Update   │
│ 4. Git Commit/Push   │
└──────────────────────┘
    ↓
GitHub Pages (auto-deploy)
```

## Support

Sorular veya sorunlar için:
1. WEBHOOK_GUIDE.md'yi kontrol et
2. Logs'ları incele
3. Test endpoints'i çalıştır
4. GitHub issues'i oluştur

---

**Son güncellenme**: 2026-01-02  
**Versiyon**: 2.0
