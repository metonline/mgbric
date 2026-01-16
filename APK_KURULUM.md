# APK Oluşturma Rehberi - EAS Build (Basit Yol)

## Seçenek 1: EAS Build (Önerilir - Kurulum Yok)

EAS Build Expo'nun **bulut tabanlı** Android/iOS build servisidir. Hiçbir kurulum gerekmez!

### Adımlar:

1. **Expo CLI yükle:**
   ```bash
   npm install -g eas-cli
   ```

2. **Projeyi Expo'ya bağla:**
   ```bash
   cd c:\Users\metin\Desktop\BRIC
   npx create-expo-app@latest turnuva-app
   ```
   Veya mevcut projeyi kullan.

3. **EAS hesabı oluştur:**
   ```bash
   eas login
   ```
   (GitHub/Google ile)

4. **APK'yı build et:**
   ```bash
   eas build --platform android --release
   ```

5. **APK'yı indir:** Build tamamlandıktan sonra link gönderilir

### Avantajlar:
- ✅ Hiçbir kurulum gerekmez
- ✅ Şu anda hızlı ve bedava
- ✅ iOS ve Android ikisi de desteklenir
- ✅ Otomatik code signing

---

## Seçenek 2: Cordova Kullan (Hızlı)

Capacitor yerine Cordova + PhoneGap kullan:

```bash
npm install -g cordova
cordova create hosgoru-app com.hosgoru.turnuva "Hoşgörü"
cd hosgoru-app
cordova platform add android
cordova build android --release
```

APK: `hosgoru-app\platforms\android\app\build\outputs\apk\release\`

---

## Seçenek 3: GitHub Actions (Otomatik)

GitHub repo oluştur ve Actions workflow ekle - Gradle otomatik build eder.

---

Hangi yolu seçmek istersin?
