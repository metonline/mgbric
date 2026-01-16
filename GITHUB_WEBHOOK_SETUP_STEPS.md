# GitHub Webhook Ekleme - Adım Adım

## 🚀 Webhook Server Çalışıyor!

✅ Server başarıyla başlatıldı  
✅ Port 5000'de dinliyor  
✅ Webhook secret konfigüre edildi  

---

## 📋 ADIM 1: ngrok ile Genel URL Oluştur (İsteğe Bağlı)

Eğer local test yapmak istiyorsan:

1. **ngrok'u indir**: https://ngrok.com/download
2. **Çalıştır**:
   ```bash
   ngrok http 5000
   ```
3. **Kopyala**: ngrok sizin HTTPS URL'sini verecek
   ```
   Forwarding: https://xxxx-xxx-xxx-xxx.ngrok.io -> http://localhost:5000
   ```

---

## 🔧 ADIM 2: GitHub'da Webhook Ekle

1. **GitHub Settings'e Git**:
   ```
   https://github.com/USERNAME/BRIC/settings/hooks
   ```

2. **"Add webhook" Butonuna Tıkla**

3. **Ayarları Doldur**:

   | Alan | Değer |
   |------|-------|
   | **Payload URL** | `https://your-domain.com/webhook` VEYA `https://ngrok-url/webhook` |
   | **Content type** | `application/json` |
   | **Secret** | `1440e61bb914225c5e80bb0e5aba7fec` |
   | **Events** | ✓ Push events (sadece bunu seç) |
   | **Active** | ✓ Checked |

4. **"Add webhook" Butonuna Tıkla**

---

## ✅ ADIM 3: Test Et

### Test 1: GitHub UI'de Test Et
```
GitHub'da webhook'u tıkla
→ "Recent Deliveries" sekmesine bak
→ İlk request'i tıkla
→ Response'ı kontrol et
```

### Test 2: Gerçek Push Yap
```bash
# BRIC repo'suna herhangi bir değişiklik yap
# Git push et

# Webhook trigger olacak
# Logs'ta "Webhook processing completed!" görülecek
```

### Test 3: Database Kontrol Et
```bash
# database.json güncellenmiş mi?
# GitHub'da commit görülüyor mu?
# Website güncellenmiş mi?
```

---

## 🔗 Webhook URL'leri

### Local Testing (ngrok)
```
https://xxxx-xxx-xxx-xxx.ngrok.io/webhook
```

### Production Examples
```
https://your-domain.com/webhook
https://your-vps.com/webhook
https://your-app.herokuapp.com/webhook
```

---

## ⚠️ Troubleshooting

**Problem**: "Could not verify the request signature"
```
→ Secret'ı kontrol et: 1440e61bb914225c5e80bb0e5aba7fec
→ GitHub webhook settings'de exact match var mı?
```

**Problem**: "Connection refused"
```
→ Webhook server çalışıyor mu?
→ Port 5000 açık mı?
→ Firewall engel koyuyor mu?
```

**Problem**: "Webhook triggered but no update"
```
→ Logs'u kontrol et
→ database.json yazılabilir mi?
→ Git credentials configured mi?
```

---

## 📊 Webhook Secret

```
1440e61bb914225c5e80bb0e5aba7fec
```

✅ Bunu GitHub'da ayarla  
⚠️ Bunu asla paylaşma  
✅ `.env.webhook` dosyasına kaydedildi

---

## 🎯 Sonraki Adımlar

1. [ ] ngrok başlat (eğer local test yapacaksan)
2. [ ] GitHub webhook'u ekle
3. [ ] Secret'ı kontrol et
4. [ ] Test push yap
5. [ ] Logs'u kontrol et
6. [ ] Database'i kontrol et

---

**Webhook server şu adreste çalışıyor:**
- `http://127.0.0.1:5000`
- `http://192.168.0.11:5000`
- `http://0.0.0.0:5000`

**GitHub Webhook URL:**
- ngrok test: `https://your-ngrok-url/webhook`
- Production: `https://your-domain.com/webhook`

---

Başladığında GitHub'da "Recent Deliveries" sekmesinde request'ler görülecek! 🚀
