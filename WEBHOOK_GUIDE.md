# GitHub Webhook Integration Guide

Kendi web sunucunuzda otomatik güncellemeler için GitHub webhook entegrasyonu.

## Özellikler

✅ **Veri Güncelleştirme**: Vugraph'tan turnuva verilerini otomatik fetch  
✅ **Tasarım Senkronizasyonu**: GitHub'dan CSS/HTML/JS dosyalarını güncelle  
✅ **Otomatik Commit**: Değişiklikleri GitHub'a geri push  
✅ **Güvenli**: HMAC-SHA256 webhook signature doğrulaması  
✅ **Loglama**: Detaylı işlem logları  

## Kurulum Adımları

### 1️⃣ Webhook Server'ı Başlatın

```powershell
# PowerShell'de
$env:GITHUB_WEBHOOK_SECRET = "your-secure-secret-here"
python webhook_server.py
```

Veya .env dosyası oluşturun:
```
GITHUB_WEBHOOK_SECRET=your-secure-secret-here
```

### 2️⃣ Webhook Secret'ı Oluşturun

```powershell
python setup_webhook.py
```

Bu komut bir secure secret oluşturacak ve GitHub setup talimatlarını verecek.

### 3️⃣ GitHub'da Webhook Yapılandırın

1. GitHub repository settings'e gidin:
   - `https://github.com/YOUR_USERNAME/BRIC/settings/hooks`

2. "Add webhook" butonuna tıklayın

3. Ayarları doldurun:
   - **Payload URL**: `https://your-server.com/webhook` (veya ngrok URL)
   - **Content type**: `application/json`
   - **Secret**: setup_webhook.py'den aldığınız secret
   - **Events**: "Just the push event" seçin
   - **Active**: Checkmark koyun

4. "Add webhook" butonuna tıklayın

### 4️⃣ Webhook'u Test Edin

```powershell
# Farklı bir terminal'de webhook server'ı çalışırken:
python test_webhook.py
```

## Nasıl Çalışır

```
GitHub Push
    ↓
Webhook trigger
    ↓
webhook_server.py
    ↓
┌─────────────────────┐
│ 1. Git pull origin   │  → En son dosyaları indir
└─────────────────────┘
    ↓
┌─────────────────────────────┐
│ 2. Vugraph data update      │  → Turnuva verisi güncelle
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│ 3. Git commit & push        │  → Değişiklikleri GitHub'a gönder
└─────────────────────────────┘
```

## Dosyalar

| Dosya | Amaç |
|-------|------|
| `webhook_server.py` | Ana webhook server (Flask) |
| `setup_webhook.py` | Webhook setup wizard |
| `test_webhook.py` | Webhook test aracı |
| `vugraph_fetcher.py` | Vugraph API veri çekme |
| `auto_update_vugraph.py` | Veri güncelleme logikleri |

## API Endpoints

### POST /webhook
GitHub webhook push events'i işler

**Headers:**
```
Content-Type: application/json
X-Hub-Signature-256: sha256=...
X-GitHub-Event: push
```

**Response:**
```json
{
  "status": "success",
  "message": "Webhook processed successfully",
  "timestamp": "2026-01-02T10:30:00.000000"
}
```

### GET /health
Server sağlık kontrolü

**Response:**
```json
{
  "status": "healthy",
  "service": "GitHub Webhook Server",
  "timestamp": "2026-01-02T10:30:00.000000"
}
```

### GET /status
Server durumu ve konfigürasyon bilgisi

**Response:**
```json
{
  "status": "running",
  "repository_path": "/path/to/repo",
  "webhook_configured": true,
  "timestamp": "2026-01-02T10:30:00.000000"
}
```

## Troubleshooting

### "Invalid webhook signature" hatası
- GitHub'da ayarladığınız secret ile çalışıyor olduğunuzun secret eşleştiğini kontrol edin
- `$env:GITHUB_WEBHOOK_SECRET` ayarlandı mı kontrol edin

### "Could not connect to webhook server" hatası
- webhook_server.py'nin çalışıp çalışmadığını kontrol edin
- Port 5000'in açık olduğunu kontrol edin: `netstat -ano | findstr :5000`

### "Git pull failed" uyarısı
- Git'in installed olduğunu kontrol edin: `git --version`
- SSH key'lerinizin configured olduğunu kontrol edin

### "Vugraph update failed" hatası
- İnternet bağlantısını kontrol edin
- Vugraph sitesine erişim sağlayıp sağlayamadığını kontrol edin
- Timeout ayarını artırabilirsiniz (webhook_server.py içinde)

## Production Deployment

### Kubernetes/Docker
```dockerfile
FROM python:3.10
RUN pip install flask requests beautifulsoup4
COPY . /app
WORKDIR /app
ENV GITHUB_WEBHOOK_SECRET=${WEBHOOK_SECRET}
CMD ["python", "webhook_server.py"]
```

### Systemd Service (Linux)
```ini
[Unit]
Description=GitHub Webhook Server
After=network.target

[Service]
Type=simple
User=appuser
WorkingDirectory=/path/to/BRIC
Environment="GITHUB_WEBHOOK_SECRET=your-secret"
ExecStart=/usr/bin/python3 webhook_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Windows Task Scheduler
```powershell
$taskName = "GitHub-Webhook-Server"
$taskDescription = "Runs GitHub webhook server for auto-updates"
$action = New-ScheduledTaskAction -Execute "C:\Python310\python.exe" -Argument "C:\path\to\webhook_server.py"
$trigger = New-ScheduledTaskTrigger -AtStartup
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -RunLevel Highest
```

## Güvenlik

⚠️ **Önemli**: 
- Webhook secret'ınızı asla GitHub'da yayınlamayın
- `.env` dosyasını `.gitignore`'a ekleyin
- Production'da HTTPS kullanın
- IP whitelist yapın (GitHub webhook IPs)

## Logs

Webhook işlemleri konsol'da ve günlük dosyasında kaydedilir:

```powershell
# Logs'u görmek için:
python webhook_server.py
```

Her işlem şu bilgileri kaydeder:
- ⏰ Timestamp
- 📝 İşlem adı
- ✅/❌ Sonuç
- 📊 Detaylar

## Örnek Log Çıktısı

```
============================================================
2026-01-02 10:30:15 🔔 GitHub Webhook Received!
Repository: username/BRIC
Branch: refs/heads/main
============================================================

2026-01-02 10:30:15 Starting update pipeline...
Step 1: Pull latest files from GitHub
2026-01-02 10:30:16 ✓ Git pull successful

Step 2: Update database from Vugraph
2026-01-02 10:30:16 Fetching tournaments from 2025-12-30 to 2026-01-09
2026-01-02 10:30:25 ✓ Database updated successfully (25 new records added)

Step 3: Commit and push changes
2026-01-02 10:30:26 ✓ Changes committed
2026-01-02 10:30:28 ✓ Changes pushed to GitHub

2026-01-02 10:30:28 ✓ Webhook processing completed!
============================================================
```

## FAQ

**S: GitHub Actions workflow'tan fark ne?**
A: Webhook server'ı kendi sunucunuzda çalıştırıyorsunuz, GitHub'ın sunucularında değil. Böylece daha fazla kontrol ve özelleştirme yapabilirsiniz.

**S: Hem webhook hem GitHub Actions'ı çalıştırabilir miyim?**
A: Evet, ama önerilmez (duplicate updates). GitHub Actions'ı disable etmek ve sadece webhook kullanmak daha iyi.

**S: Webhook'un 24/7 çalışması gerekir mi?**
A: Evet. Continuous deployment için sunucu her zaman açık olmalı. Veya ngrok/Cloudflare Tunnel kullanabilirsiniz.

**S: GitHub down olursa ne olur?**
A: Webhook'tan veri fetch edilemeyecek. Logs'ta error görünecek. Tekrar online olduğunda otomatik retry yapılacak.

## Support

Hata veya soru için:
1. Logs'ları kontrol edin
2. test_webhook.py'yi çalıştırın
3. `/health` endpoint'ini kontrol edin

---

**Son güncellenme**: 2026-01-02  
**Versiyon**: 1.0
