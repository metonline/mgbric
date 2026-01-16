# GitHub Actions - Automatic APK Build Setup

## Status
✅ Workflow created at: `.github/workflows/android-build.yml`

## How it Works

1. **Push to GitHub** → Automatic trigger
2. **GitHub Actions runs** → Builds Android APK
3. **APK auto-uploaded** → Available in Releases

## Next Steps

### Step 1: Create New Repository on GitHub
```
https://github.com/new
Repository name: hosgoru-app
Description: Hoşgörü Turnuva Analizi Mobile App
Public: ✓
```

### Step 2: Push Local Code to GitHub

**Using GitHub Desktop:**
1. Open GitHub Desktop
2. File → Add Local Repository
3. Path: `c:\Users\metin\Desktop\hosgoru-app`
4. Publish repository → Select account (metonline)
5. Name: `hosgoru-app`
6. Publish

**Or using Command Line:**
```powershell
cd c:\Users\metin\Desktop\hosgoru-app
git init
git add .
git commit -m "Initial Cordova app"
git branch -M main
git remote add origin https://github.com/metonline/hosgoru-app.git
git push -u origin main
```

### Step 3: GitHub Actions Builds Automatically
- Go to your repo → Actions tab
- Watch the build progress
- Download APK from Artifacts when done

### Step 4: Install on Android Phone
- Download APK from Releases
- Transfer to phone
- Install

## File Structure
```
hosgoru-app/
├── www/
│   ├── index.html
│   ├── script.js
│   ├── style.css
│   ├── database.json
│   └── ... (all files)
├── .github/
│   └── workflows/
│       └── android-build.yml  ✅ Created
├── cordova/
├── platforms/
│   └── android/
└── config.xml
```

## Expected Output
- Build log in GitHub Actions
- APK file: `hosgoru-app-release.apk`
- Release page with download link

---

**Ready to push? Start with Step 1!**
