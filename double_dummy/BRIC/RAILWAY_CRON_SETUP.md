# Railway Cron Job Setup Instructions

## 🚂 Railway URL
**URL**: `https://mgbric.up.railway.app`

## ⚠️ Önce Railway'i Güncelle!

Railway'deki kodunuz eski - webhook endpoint'leri yok. Güncellemek için:

```bash
git add .
git commit -m "Add webhook endpoints for auto-update"
git push
```

Railway otomatik deploy edecek.

## 🔧 Railway Environment Variable Ekle

Railway Dashboard > Variables:
```
WEBHOOK_SECRET=bric-update-secret-2026
```

---

## 🕐 Cron-Job.org ile Otomatik Güncelleme (ÜCRETSİZ)

1. https://cron-job.org adresine git
2. Ücretsiz hesap aç
3. Aşağıdaki cron job'ları ekle:

### Cron Job Listesi

| Saat (TR) | Cron Expression | URL |
|-----------|-----------------|-----|
| 10:00 | `0 7 * * *` | `https://mgbric.up.railway.app/api/cron/update?secret=bric-update-secret-2026` |
| 12:00 | `0 9 * * *` | `https://mgbric.up.railway.app/api/cron/update?secret=bric-update-secret-2026` |
| 16:00 | `0 13 * * *` | `https://mgbric.up.railway.app/api/cron/update?secret=bric-update-secret-2026` |
| 17:15 | `15 14 * * *` | `https://mgbric.up.railway.app/api/cron/update?secret=bric-update-secret-2026` |
| 17:20 | `20 14 * * *` | `https://mgbric.up.railway.app/api/cron/update?secret=bric-update-secret-2026` |
| 17:25 | `25 14 * * *` | `https://mgbric.up.railway.app/api/cron/update?secret=bric-update-secret-2026` |
| 17:30 | `30 14 * * *` | `https://mgbric.up.railway.app/api/cron/update?secret=bric-update-secret-2026` |
| 17:35 | `35 14 * * *` | `https://mgbric.up.railway.app/api/cron/update?secret=bric-update-secret-2026` |
| 17:40 | `40 14 * * *` | `https://mgbric.up.railway.app/api/cron/update?secret=bric-update-secret-2026` |
| 17:45 | `45 14 * * *` | `https://mgbric.up.railway.app/api/cron/update?secret=bric-update-secret-2026` |
| 17:50 | `50 14 * * *` | `https://mgbric.up.railway.app/api/cron/update?secret=bric-update-secret-2026` |
| 17:55 | `55 14 * * *` | `https://mgbric.up.railway.app/api/cron/update?secret=bric-update-secret-2026` |
| 18:00 | `0 15 * * *` | `https://mgbric.up.railway.app/api/cron/update?secret=bric-update-secret-2026` |
| 23:55 | `55 20 * * *` | `https://mgbric.up.railway.app/api/cron/update?secret=bric-update-secret-2026` |

---

## ⏰ Zamanlama Özeti

| Türkiye Saati | UTC Saati | Açıklama |
|---------------|-----------|----------|
| 10:00 | 07:00 | Sabah güncellemesi |
| 12:00 | 09:00 | Öğlen güncellemesi |
| 16:00 | 13:00 | Öğleden sonra |
| 17:15-18:00 | 14:15-15:00 | Turnuva saati (her 5 dk) |
| 23:55 | 20:55 | Gece final senkronizasyonu |

---

## 🔧 Environment Variables (Railway'de ayarla)

```
WEBHOOK_SECRET=bric-update-secret-2026
```

Bu secret'ı Railway dashboard > Variables bölümüne ekle.

---

## 🧪 Test Etme

### Webhook Test:
```bash
curl -X POST https://YOUR-APP.railway.app/api/webhook/update \
  -H "X-Webhook-Secret: bric-update-secret-2026" \
  -H "Content-Type: application/json" \
  -d '{"type":"all"}'
```

### Status Kontrol:
```bash
curl https://YOUR-APP.railway.app/api/webhook/status
```

### Cron Endpoint Test:
```bash
curl "https://YOUR-APP.railway.app/api/cron/update?secret=bric-update-secret-2026&type=all"
```

---

## 📝 Notlar

1. **Railway Free Tier:** Cron job'lar sınırlı olabilir
2. **Timeout:** Update işlemi 10 dakikaya kadar sürebilir, Railway timeout'a dikkat et
3. **Logging:** Update logları `update_log.txt` dosyasına yazılır
4. **Windows Task Scheduler:** Yerel bilgisayardan da tetikleme yapılabilir (setup_multi_schedule.ps1)

---

## 🔗 API Endpoints

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/api/webhook/update` | POST | Ana güncelleme endpoint'i |
| `/api/webhook/status` | GET | Database durumu |
| `/api/cron/update` | GET/POST | Cron için basit endpoint |

### Request Body (opsiyonel):
```json
{
  "type": "all"  // "all", "scores", veya "hands"
}
```
