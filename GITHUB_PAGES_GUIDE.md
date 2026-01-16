# GitHub Pages Yayınlama Adımları

## Adım 1: GitHub Hesabı & Repository

1. **GitHub'a giriş yap:** https://github.com/login
2. **Yeni repository oluştur:**
   - Adı: `hosgoru-pwa` (veya istediğin ad)
   - Public seç
   - README ekleme ✅
   - Create

## Adım 2: Git Ayarları

```powershell
# Git config
git config --global user.name "Senin Adın"
git config --global user.email "senin@email.com"
```

## Adım 3: BRIC Klasörünü Hazırla

```powershell
cd c:\Users\metin\Desktop\BRIC

# Repository başlat
git init
git add .
git commit -m "Initial PWA commit"
git branch -M main

# Remote bağla (REPO_URL yerine GitHub URL'ini koy)
git remote add origin https://github.com/KULLANICI_ADI/hosgoru-pwa.git
git push -u origin main
```

## Adım 4: GitHub Pages Aktif Et

GitHub'da repo ayarlarında:
- **Settings** → **Pages**
- Source: `main` branch seç
- Save

**URL alacaksın:** `https://KULLANICI_ADI.github.io/hosgoru-pwa/`

## Adım 5: index.html Kontrol

`index.html`'de referanslar mutlak yol mu, göreceli mi kontrol et:
- ❌ Bad: `/script.js`
- ✅ Good: `./script.js`

---

## Hızlı Komut Özetl

```powershell
cd c:\Users\metin\Desktop\BRIC
git init
git add .
git commit -m "PWA commit"
git branch -M main
git remote add origin https://github.com/KULLANICI/hosgoru-pwa.git
git push -u origin main
```

**GitHub → Settings → Pages → main branch seç → Bitti!**

---

**Sonrası:** Telefondan açıp "Uygulamayı Yükle" seçip PWA kuracaksın!
