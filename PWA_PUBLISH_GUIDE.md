# PWA Yayınlama Rehberi

## Hızlı Yol: Netlify Drop (En Basit)

1. **Tarayıcıda aç:**
   https://app.netlify.com/drop

2. **Bir klasör oluştur** (örn: `pwa-hosgoru`):
   - index.html
   - script.js
   - style.css
   - manifest.json
   - tr.json
   - en.json
   - database.json
   - database_temp.json
   - *.png, *.jpeg dosyaları

3. **Klasörü Netlify'ye sürükle-bırak**

4. **Otomatik URL alacaksın** (örn: `https://xyz-pwa.netlify.app`)

5. **Mobilde test et:**
   - Chrome: Adresi aç → Menü → "Ekrana yükle"
   - Safari: Paylaş → "Ana Ekrana Ekle"

---

## Alternatif: GitHub Pages

Eğer GitHub hesabın varsa:

```bash
# Git kur (Windows)
# https://git-scm.com/download/win indir ve kur

git init
git add .
git commit -m "Initial PWA commit"
git branch -M main
git remote add origin https://github.com/KULLANICI_ADI/hosgoru-pwa.git
git push -u origin main
```

**GitHub ayarları:**
- Settings → Pages → Source: main branch
- Custom domain (opsiyonel)

---

## Manifest.json Kontrol Listesi

✅ Mevcut ayarlar:
- name: "Hoşgörü Turnuva Analiz Paneli"
- short_name: "Turnuva Analizi"
- start_url: "/index.html"
- display: "standalone"
- theme_color: "#1e3c72"
- background_color: "#ffffff"
- icons: [SVG logos var]

✅ Service Worker (sw.js) var
✅ PWA desteği tam

---

## Hangi Yolu Seçmek İstiyorsun?

**Seçenek 1: Netlify Drop (Tavsiye)**
- Hiçbir kurulum yok
- 5 dakika
- Ücretsiz

**Seçenek 2: GitHub Pages**
- Ücretsiz
- Git gerekli
- Custom domain işi kolay

**Seçenek 3: Vercel**
- Zeit'in yeni adı
- Nextjs friendly
- Ücretsiz + Pro versiyonu var

Hangi platformu kullanmak istersin?
