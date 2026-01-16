// Script version for cache busting - v377
const SCRIPT_VERSION = '377';

// ===== DİL SISTEMI (i18n) =====
let translations = {};
let currentLanguage = localStorage.getItem('appLanguage') || 'tr';

// Çevirileri yükle
async function loadTranslations(lang) {
    try {
        const response = await fetch(`./` + lang + `.json?v=` + Date.now());
        if (response.ok) {
            const data = await response.json();
            translations[lang] = data;
            console.log(`✓ ${lang.toUpperCase()} çeviriler yüklendi (${Object.keys(data).length} key)`);
            return true;
        } else {
            console.error(`❌ ${lang.toUpperCase()} dosyası bulunamadı (HTTP ${response.status})`);
            return false;
        }
    } catch (e) {
        console.error(`❌ ${lang.toUpperCase()} çeviriler yüklenemedi:`, e.message);
        return false;
    }
}

// Belirli bir çeviriye erişimi
function getTranslation(keyPath) {
    // Eğer çeviriler yüklenmemişse, anahtar döndür
    if (!currentLanguage || !translations[currentLanguage]) {
        console.warn(`⚠️ Çeviriler henüz yüklenmemiş. Lang: ${currentLanguage}, Translations:`, Object.keys(translations));
        return keyPath;
    }
    
    let value = translations[currentLanguage];
    const keys = keyPath.split('.');
    
    for (let key of keys) {
        if (value && typeof value === 'object') {
            value = value[key];
        } else {
            return keyPath; // Çeviri bulunamadıysa anahtar döndür
        }
    }
    
    return value || keyPath;
}

// Dosya bilgisini göster (dil değişiklikleri için dinamik)
function updateFileInfo() {
    if (!allData || allData.length === 0) {
        return;
    }
    const lastDate = getLastDateFromDatabase();
    const msg = getTranslation('results.databaseUpdated')
        .replace('{date}', lastDate)
        .replace('{count}', allData.length);
    document.getElementById('fileInfo').innerHTML = `<span style='color:green;'>${msg}</span>`;
}

// Database'deki en son tarihi al (DD.MM.YY formatında)
function getLastDateFromDatabase() {
    if (!allData || allData.length === 0) {
        return 'N/A';
    }
    
    // Tüm tarihleri al ve sırala
    const dates = [...new Set(allData.map(r => r.Tarih))].filter(d => d);
    if (dates.length === 0) return 'N/A';
    
    // DD.MM.YYYY formatını karşılaştır için sayıya dönüştür
    const sortedDates = dates.sort((a, b) => {
        const [da, doa, ya] = a.split('.').map(Number);
        const [db, dob, yb] = b.split('.').map(Number);
        const dateA = ya * 10000 + doa * 100 + da;
        const dateB = yb * 10000 + dob * 100 + db;
        return dateB - dateA; // En yenisi ilk
    });
    
    // DD.MM.YY formatına dönüştür
    const lastDate = sortedDates[0]; // En son (en yeni) tarih
    const [d, mo, y] = lastDate.split('.').map(Number);
    const yy = String(y).slice(-2);
    const dateFormatted = `${String(d).padStart(2, '0')}.${String(mo).padStart(2, '0')}.${yy}`;
    return dateFormatted;
}

// Dili değiştir ve sayfayı güncelle
function switchLanguage(lang) {
    console.log(`🔄 switchLanguage('${lang}') çağrıldı`);
    
    // Çeviriler yüklenmemişse yükle
    if (!translations[lang] || Object.keys(translations[lang] || {}).length === 0) {
        console.warn(`⚠️ ${lang} çeviriler yüklenmedi, yükleniyor...`);
        loadTranslations(lang).then(() => {
            console.log(`✓ ${lang} çeviriler yüklendi, tekrar dene`);
            switchLanguage(lang);
        });
        return;
    }
    
    currentLanguage = lang;
    localStorage.setItem('appLanguage', lang);
    console.log(`✓ currentLanguage = '${lang}', localStorage kaydedildi`);
    
    // Dil butonlarının opacity'sini güncelle
    const trBtn = document.getElementById('langBtn-tr');
    const enBtn = document.getElementById('langBtn-en');
    
    if (trBtn) {
        trBtn.style.opacity = lang === 'tr' ? '1' : '0.5';
        console.log(`✓ TR butonu opacity: ${lang === 'tr' ? '1' : '0.5'}`);
    }
    if (enBtn) {
        enBtn.style.opacity = lang === 'en' ? '1' : '0.5';
        console.log(`✓ EN butonu opacity: ${lang === 'en' ? '1' : '0.5'}`);
    }
    
    // data-i18n attribute'li öğeleri güncelle
    const elementsToTranslate = document.querySelectorAll('[data-i18n]');
    console.log(`📝 Çevrilecek öğe sayısı: ${elementsToTranslate.length}`);
    
    elementsToTranslate.forEach((el, idx) => {
        const key = el.getAttribute('data-i18n');
        const translated = getTranslation(key);
        el.textContent = translated;
        if (idx < 3) console.log(`   [${idx}] ${key} → ${translated}`);
    });
    
    // data-i18n-placeholder attribute'li öğeleri güncelle
    const placeholderElements = document.querySelectorAll('[data-i18n-placeholder]');
    placeholderElements.forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        el.placeholder = getTranslation(key);
    });
    
    // Belirli ID'li öğeleri manuel olarak çevir
    const translationMap = {
        'pageTitle': 'header.title',
        'pageSubtitle': 'header.subtitle',
        'statsSection': 'stats.title'
    };
    
    Object.entries(translationMap).forEach(([id, key]) => {
        const el = document.getElementById(id);
        if (el) {
            el.textContent = getTranslation(key);
            console.log(`✓ ID '${id}' çevrildi`);
        }
    });
    
    // Privacy Policy link'ini güncelle
    const privacyLinkTr = document.getElementById('privacyLink-tr');
    const privacyLinkEn = document.getElementById('privacyLink-en');
    if (privacyLinkTr) privacyLinkTr.style.display = lang === 'tr' ? 'inline' : 'none';
    if (privacyLinkEn) privacyLinkEn.style.display = lang === 'en' ? 'inline' : 'none';
    
    // Dosya bilgisini güncelle (dil değişikliği için)
    updateFileInfo();
    
    console.log(`✅ Dil değiştirildi: ${lang.toUpperCase()}`);
}

// Dil sistemini başlat
async function initLanguage() {
    console.log('🌐 Dil sistemi başlatılıyor...');
    
    try {
        await loadTranslations('tr');
        await loadTranslations('en');
        
        // Başlangıç dilini ayarla
        currentLanguage = localStorage.getItem('appLanguage') || 'tr';
        console.log(`✓ Başlangıç dili: ${currentLanguage.toUpperCase()}`);
        
        // Sayfayı çevir
        await new Promise(resolve => setTimeout(resolve, 100)); // Kısa delay
        switchLanguage(currentLanguage);
        
        // Tarih input'unun default değerini en son veri güncelleme tarihine ayarla
        const selectedDateInput = document.getElementById('selectedDate');
        if (selectedDateInput) {
            try {
                // Database'den en son tarihi al
                const response = await fetch('database.json');
                const data = await response.json();
                
                if (data && data.length > 0) {
                    // Database sonda en yeni tarih var (eski -> yeni sıralanmış)
                    const latestRecord = data[data.length - 1];
                    const latestDateStr = latestRecord.Tarih; // Format: "02.01.2026"
                    
                    if (latestDateStr) {
                        // DD.MM.YYYY -> YYYY-MM-DD dönüştür
                        const [day, month, year] = latestDateStr.split('.');
                        const inputDateValue = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
                        selectedDateInput.value = inputDateValue;
                        console.log(`✓ Tarih input'u en son güncelleme tarihine ayarlandı: ${inputDateValue} (${latestDateStr})`);
                    }
                } else {
                    throw new Error('Database boş');
                }
            } catch (err) {
                console.warn(`⚠️ Database tarih alınamadı, bugünün bir önceki günü kullan. Hata: ${err.message}`);
                // Fallback: bugünün bir gün öncesi
                const now = new Date();
                const yesterday = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1);
                const yyyy = yesterday.getFullYear();
                const mm = String(yesterday.getMonth() + 1).padStart(2, '0');
                const dd = String(yesterday.getDate()).padStart(2, '0');
                selectedDateInput.value = `${yyyy}-${mm}-${dd}`;
                console.log(`✓ Fallback tarih kullanıldı: ${yyyy}-${mm}-${dd}`);
            }
        }
        
        console.log(`✓ Dil sistemi başarıyla başlatıldı`);
    } catch (e) {
        console.error('❌ Dil sistemi başlatma hatası:', e);
    }
}

// ===== PLAYER AUTOCOMPLETE SEARCH =====
let allPlayers = [];

// Türkçe karakterleri normalize et (İ→i, Ş→s vs)
function normalizeText(text) {
    const turkishChars = {
        'Ç': 'c', 'ç': 'c',
        'Ğ': 'g', 'ğ': 'g',
        'İ': 'i', 'ı': 'i',
        'Ö': 'o', 'ö': 'o',
        'Ş': 's', 'ş': 's',
        'Ü': 'u', 'ü': 'u'
    };
    return text.replace(/./g, char => turkishChars[char] || char).toLowerCase();
}

function initializePlayerSearch() {
    if (allData.length === 0) return;
    
    // Tüm oyuncu adlarını topla ve normalize et
    const players = new Set();
    allData.forEach(record => {
        if (record['Oyuncu 1']) players.add(record['Oyuncu 1'].trim().replace(/\s+/g, ' '));
        if (record['Oyuncu 2']) players.add(record['Oyuncu 2'].trim().replace(/\s+/g, ' '));
    });
    
    allPlayers = Array.from(players).sort();
    
    console.log('allPlayers toplamda:', allPlayers.length);
    
    // playerName input'una listener ekle
    const playerInput = document.getElementById('playerName');
    if (playerInput) {
        playerInput.addEventListener('input', function(e) {
            const query = e.target.value.trim().toLowerCase();
            const dropdown = document.getElementById('playerNameSuggestions');
            
            if (query.length === 0) {
                dropdown.style.display = 'none';
                dropdown.innerHTML = '';
                return;
            }
            
            // Filtreleme - max 5 sonuç
            const filtered = allPlayers.filter(player => 
                player.toLowerCase().includes(query)
            ).slice(0, 5);
            
            if (filtered.length === 0) {
                dropdown.style.display = 'none';
                dropdown.innerHTML = '';
                return;
            }
            
            // Dropdown'u doldur
            dropdown.innerHTML = filtered.map((player, idx) => `
                <div style='padding:10px 12px;cursor:pointer;border-bottom:1px solid #f0f0f0;background:${idx % 2 === 0 ? 'white' : '#f9f9f9'};transition:background 0.2s;' 
                     onmouseover="this.style.background='#e8f0fe'" 
                     onmouseout="this.style.background='${idx % 2 === 0 ? 'white' : '#f9f9f9'}'"
                     onclick="selectPlayerName('${player.replace(/'/g, "\\'")}')">${player}</div>
            `).join('');
            
            dropdown.style.display = 'block';
        });
        
        // Input dışında tıklandığında dropdown'u kapat
        document.addEventListener('click', function(e) {
            if (e.target !== playerInput) {
                document.getElementById('playerNameSuggestions').style.display = 'none';
            }
        });
    }
}

// ===== QUICK DATE FILTER BUTTON HANDLER =====
function setDateRangeFilter(period, event) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    // Database hazır değilse bekle
    if (!databaseReady || !allData || allData.length === 0) {
        console.log(`⏳ Veritabanı henüz hazır değil, ${period} filter bekleniyor...`);
        setTimeout(() => setDateRangeFilter(period, null), 100);
        return;
    }
    
    console.log(`🔔 setDateRangeFilter('${period}') çağrıldı`);
    window.period = period;
    loadDatabase(period);  // loadDatabase zaten openGlobalRangeModal çağırır
}
// ===== MOBILE MODAL PAGE NAVIGATION (3 Sayfa) =====
function goToNextPage() {
    const pagesContainer = document.getElementById('pagesContainer');
    const currentPage = document.getElementById('currentPage');
    if (!pagesContainer || !currentPage) return;
    let page = parseInt(currentPage.textContent, 10);
    if (page < 3) {
        page++;
        pagesContainer.style.transform = `translateX(-${(page-1)*100}%)`;
        currentPage.textContent = page;
        updateMobilePageButtons();
    }
}

function goToPreviousPage() {
    const pagesContainer = document.getElementById('pagesContainer');
    const currentPage = document.getElementById('currentPage');
    if (!pagesContainer || !currentPage) return;
    let page = parseInt(currentPage.textContent, 10);
    if (page > 1) {
        page--;
        pagesContainer.style.transform = `translateX(-${(page-1)*100}%)`;
        currentPage.textContent = page;
        updateMobilePageButtons();
    }
}

function updateMobilePageButtons() {
    const currentPage = parseInt(document.getElementById('currentPage').textContent, 10);
    const prevBtn = document.querySelector('#resultsNavigation button:first-child');
    const nextBtn = document.querySelector('#resultsNavigation button:last-child');
    
    if (prevBtn) prevBtn.style.visibility = currentPage === 1 ? 'hidden' : 'visible';
    if (nextBtn) nextBtn.style.visibility = currentPage === 3 ? 'hidden' : 'visible';
}

// ===== SWIPE NAVIGATION =====
function initSwipeNavigation() {
    const mobileModal = document.getElementById('mobileResultsModal');
    if (!mobileModal) {
        console.warn('⚠️ mobileResultsModal bulunamadı');
        return;
    }
    
    let touchStartX = 0;
    let touchStartY = 0;
    let touchEndX = 0;
    let touchEndY = 0;
    let isSwiping = false;
    
    console.log('✓ Swipe navigation initialized');
    
    mobileModal.addEventListener('touchstart', (e) => {
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
        isSwiping = true;
        console.log('touchstart:', touchStartX, touchStartY);
    });
    
    mobileModal.addEventListener('touchmove', (e) => {
        if (!isSwiping) return;
        // Prevent default scroll behavior during swipe
        if (Math.abs(e.touches[0].clientX - touchStartX) > 10) {
            e.preventDefault();
        }
    });
    
    mobileModal.addEventListener('touchend', (e) => {
        if (!isSwiping) return;
        isSwiping = false;
        
        touchEndX = e.changedTouches[0].clientX;
        touchEndY = e.changedTouches[0].clientY;
        console.log('touchend:', touchEndX, touchEndY);
        handleSwipe();
    });
    
    function handleSwipe() {
        const swipeThreshold = 40; // Reduced threshold for better sensitivity
        const verticalThreshold = 40;
        
        const diffX = touchStartX - touchEndX;
        const diffY = Math.abs(touchStartY - touchEndY);
        
        console.log('Swipe analysis - diffX:', diffX, 'diffY:', diffY, 'threshold:', swipeThreshold);
        
        // Vertical movement daha fazla ise (scroll) swipe olarak sayma
        if (diffY > verticalThreshold) {
            console.log('⚠️ Vertical movement detected, ignoring swipe');
            return;
        }
        
        // Minimum horizontal movement gerekli
        if (Math.abs(diffX) < swipeThreshold) {
            console.log('⚠️ Swipe too small, ignoring');
            return;
        }
        
        // Sola swipe (diffX positive) → Sonraki sayfa
        if (diffX > swipeThreshold) {
            console.log('🔄 Sola swipe (diffX:', diffX, ') - Sonraki sayfa');
            const nextBtn = document.getElementById('dailyNextBtn');
            if (nextBtn) {
                console.log('✓ Clicked nextBtn');
                nextBtn.click();
            }
        }
        // Sağa swipe (diffX negative) → Önceki sayfa
        else if (diffX < -swipeThreshold) {
            console.log('🔄 Sağa swipe (diffX:', diffX, ') - Önceki sayfa');
            const prevBtn = document.getElementById('dailyPrevBtn');
            if (prevBtn) {
                console.log('✓ Clicked prevBtn');
                prevBtn.click();
            }
        }
    }
}
// ===== MOBILE MODAL CLOSING =====
function closeMobileModal() {
    const mobileModal = document.getElementById('mobileResultsModal');
    if (mobileModal) {
        mobileModal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}
// Removed illegal top-level return statements
    // ===== RENDER PAGE 3 (EW) =====
    // ===== RENDER PAGE 1 (Champions) =====
    function renderGlobalPage1() {
        if (!databaseReady) {
            setTimeout(renderGlobalPage1, 100);
            return;
        }
        let content = document.getElementById('globalModalContent');
        if (!content) return;
        content.innerHTML = `<h2 style="text-align:center;color:#1e3c72;margin:16px 0 20px 0;font-size:1.2em;">👑 Günün Şampiyonları</h2><div id="statsGrid"></div>`;
        displayChampions(globalModalData);
        const footer = document.getElementById('globalNavFooter');
        if (footer) {
            footer.style.display = 'flex';
            footer.innerHTML = `<button onclick="goToGlobalPage(-1, event)" style="flex:1;padding:10px;background:#17a2b8;color:white;border:none;cursor:pointer;margin:5px;">← Önceki</button><div style="flex:1;text-align:center;padding:10px;background:#f0f0f0;margin:5px;border-radius:4px;">Sayfa 1/3</div><button onclick="goToGlobalPage(1, event)" style="flex:1;padding:10px;background:#1e3c72;color:white;border:none;cursor:pointer;margin:5px;">Sonraki →</button>`;
        }
    }

    // ===== RENDER PAGE 2 (NS Results) =====
    function renderGlobalPage2() {
        if (!databaseReady) {
            setTimeout(renderGlobalPage2, 100);
            return;
        }
        let content = document.getElementById('globalModalContent');
        if (!content) return;
        let color = '#1ca7c1';
        let bg = '#eaf6fb';
        let title = 'Kuzey-Güney Sonuçları';
        const filtered = globalModalData.filter(row => row['Direction'] === 'NS');
        let html = `<h2 style="text-align:center;color:${color};margin:16px 0 20px 0;font-size:1.2em;">${title}</h2>`;
        filtered.forEach(row => {
            html += `<div style="background:${bg};border-radius:8px;padding:12px 16px;margin-bottom:12px;">`;
            html += `<div style="font-weight:bold;">[${row['Sıra']}] ${row['Oyuncu 1']} - ${row['Oyuncu 2']}</div>`;
            html += `<div style="color:${color};">% ${row['Skor']}</div>`;
            html += `</div>`;
        });
        if (filtered.length === 0) {
            html += `<div style='text-align:center;color:#999;font-size:1.1em;margin-top:24px;'>Sonuç bulunamadı.</div>`;
        }
        content.innerHTML = html;
        const footer = document.getElementById('globalNavFooter');
        if (footer) {
            footer.style.display = 'flex';
            footer.innerHTML = `<button onclick="goToGlobalPage(-1, event)" style="flex:1;padding:10px;background:#17a2b8;color:white;border:none;cursor:pointer;margin:5px;">← Önceki</button><div style="flex:1;text-align:center;padding:10px;background:#f0f0f0;margin:5px;border-radius:4px;">Sayfa 2/3</div><button onclick="goToGlobalPage(1, event)" style="flex:1;padding:10px;background:#6db66d;color:white;border:none;cursor:pointer;margin:5px;">Sonraki →</button>`;
        }
    }

    // ===== RENDER PAGE 3 (EW Results) =====
    function renderGlobalPage3() {
        if (!databaseReady) {
            setTimeout(renderGlobalPage3, 100);
            return;
        }
        let content = document.getElementById('globalModalContent');
        if (!content) return;
        let color = '#6db66d';
        let bg = '#f0faea';
        let title = 'Doğu-Batı Sonuçları';
        const filtered = globalModalData.filter(row => row['Direction'] === 'EW');
        let html = `<h2 style=\"text-align:center;color:${color};margin:16px 0 20px 0;font-size:1.2em;\">${title}</h2>`;
        filtered.forEach(row => {
            html += `<div style=\"background:${bg};border-radius:8px;padding:12px 16px;margin-bottom:12px;\">`;
            html += `<div style=\"font-weight:bold;\">[${row['Sıra']}] ${row['Oyuncu 1']} - ${row['Oyuncu 2']}</div>`;
            html += `<div style=\"color:${color};\">% ${row['Skor']}</div>`;
            html += `</div>`;
        });
        if (filtered.length === 0) {
            html += `<div style='text-align:center;color:#999;font-size:1.1em;margin-top:24px;'>Sonuç bulunamadı.</div>`;
        }
        content.innerHTML = html;
        const footer = document.getElementById('globalNavFooter');
        if (footer) {
            footer.style.display = 'flex';
            footer.innerHTML = `<button onclick=\"goToGlobalPage(-1, event)\" style=\"flex:1;padding:10px;background:#17a2b8;color:white;border:none;cursor:pointer;margin:5px;\">← Önceki</button><div style=\"flex:1;text-align:center;padding:10px;background:#f0f0f0;margin:5px;border-radius:4px;\">Sayfa 3/3</div><button onclick=\"closeGlobalStatsModal()\" style=\"flex:1;padding:10px;background:#6c757d;color:white;border:none;cursor:pointer;margin:5px;\">Kapat ✕</button>`;
        }
    }
// Günün Şampiyonlarını Göster (NS/EW ayrı kartlar)
function displayChampions(data) {
    if (!databaseReady) {
        // Wait for database, then re-run
        setTimeout(() => displayChampions(data), 100);
        return;
    }
    const champions = data.filter(row => row['Sıra'] == 1);
    const statsSection = document.getElementById('statsSection');
    const statsGrid = document.getElementById('statsGrid');
    if (!statsSection || !statsGrid) return;
    if (champions.length === 0) {
        statsSection.style.display = 'none';
        return;
    }
    statsSection.style.display = 'block';
    statsGrid.innerHTML = '';
    // NS ve EW gruplama
    const nsChamps = champions.filter(c => c['Direction'] === 'NS');
    const ewChamps = champions.filter(c => c['Direction'] === 'EW');
    // NS kutu
    let nsHTML = `<div style="background:#eaf6fb;border-radius:8px;padding:12px 16px;margin-bottom:12px;">
        <div style="color:#1ca7c1;font-weight:bold;font-size:1.1em;">Kuzey-Güney</div>`;
    nsChamps.forEach(champ => {
        nsHTML += `<div style="font-weight:bold;">${champ['Oyuncu 1']} - ${champ['Oyuncu 2']}</div><div style="color:#1ca7c1;">% ${champ['Skor']}</div>`;
    });
    nsHTML += `</div>`;
    // EW kutu
    let ewHTML = `<div style="background:#f0faea;border-radius:8px;padding:12px 16px;margin-bottom:12px;">
        <div style="color:#6db66d;font-weight:bold;font-size:1.1em;">Doğu-Batı</div>`;
    ewChamps.forEach(champ => {
        ewHTML += `<div style="font-weight:bold;">${champ['Oyuncu 1']} - ${champ['Oyuncu 2']}</div><div style="color:#6db66d;">% ${champ['Skor']}</div>`;
    });
    ewHTML += `</div>`;
    statsGrid.innerHTML = `<div>${nsHTML}${ewHTML}</div>`;
}

// Yön Bazında Sonuçları Göster (NS/EW ayrı)
function displayDirectionResults(data, direction) {
    if (!databaseReady) {
        setTimeout(() => displayDirectionResults(data, direction), 100);
        return;
    }
    const resultsSection = document.getElementById('directionResultsSection');
    const resultsGrid = document.getElementById('directionResultsGrid');
    const filtered = data.filter(row => row['Direction'] === direction);
    console.log(`Modal page (${direction}): ${filtered.length} kayıt bulundu.`);
    let color = direction === 'NS' ? '#1ca7c1' : '#6db66d';
    let bg = direction === 'NS' ? '#eaf6fb' : '#f0faea';
    let title = direction === 'NS' ? 'Kuzey-Güney Sonuçları' : 'Doğu-Batı Sonuçları';
    let html = `<div style="background:${bg};border-radius:8px;padding:12px 8px 8px 8px;margin-bottom:12px;">
        <div style="color:${color};font-weight:bold;font-size:1.1em;text-align:center;margin-bottom:10px;">${title}</div>`;
    filtered.forEach(row => {
        html += `<div style="background:white;border-radius:6px;padding:8px 10px;margin-bottom:8px;border-left:4px solid ${color};">
            <span style="font-weight:bold;">[${row['Sıra']}] ${row['Oyuncu 1']} - ${row['Oyuncu 2']}</span><br>
            <span style="color:${color};font-size:1em;">% ${row['Skor']}</span>
        </div>`;
    });
    html += `</div>`;
    if (filtered.length === 0) {
        html += `<div style='text-align:center;color:#999;font-size:1.1em;margin-top:24px;'>Sonuç bulunamadı.</div>`;
    }
    if (resultsGrid) {
        resultsSection.style.display = 'block';
        resultsGrid.innerHTML = html;
    } else {
        // Fallback: render directly into modal content
        const modalContent = document.getElementById('globalModalContent');
        if (modalContent) modalContent.innerHTML = html;
    }
}
// ===== GLOBAL VARIABLES =====
let allData = [];
let databaseReady = false;
let queuedModalOpen = null;
// Tarih karşılaştırma yardımcı fonksiyonu (DD.MM.YYYY formatı için)
function compareDates(dateStr, startDate, endDate) {
    // dateStr: 'DD.MM.YYYY'
    const [day, month, year] = dateStr.split('.').map(Number);
    const d = new Date(year, month - 1, day);
    return d >= startDate && d <= endDate;
}
let globalModalData = [];
let currentGlobalPage = 1;
const currentLang = 'tr';

// ===== DATABASE LOADING =====
function loadDatabase(period) {
    // Veritabanı hazır mı kontrol et
    if (!databaseReady || !allData || allData.length === 0) {
        setTimeout(() => loadDatabase(period), 100);
        return;
    }
    
    // Period belirtilmemişse window.period'u kullan
    if (!period) {
        period = window.period || 'currentMonth';
    }
    
    // Varsayılan değerler
    if (!period) {
        period = window.period || 'currentMonth';  // Parametre yoksa window.period'u kullan
    }
    let today = new Date();
    let startDate, endDate;

    // Sabit tarih aralıkları
    if (period === 'currentMonth') {
        // Bu Ay: Bugünkü ay ve yıl
        const currentMonth = today.getMonth();
        const currentYear = today.getFullYear();
        startDate = new Date(currentYear, currentMonth, 1);
        endDate = new Date(currentYear, currentMonth + 1, 0);
    } else if (period === 'currentYear') {
        // Bu Yıl: 01.01.bugünYılı - 31.12.bugünYılı
        startDate = new Date(today.getFullYear(), 0, 1);
        endDate = new Date(today.getFullYear(), 11, 31);
    } else if (period === 'last3Years') {
        // Son 3 Yıl: 01.01.(bugünYılı-2) - 31.12.bugünYılı
        startDate = new Date(today.getFullYear() - 2, 0, 1);
        endDate = new Date(today.getFullYear(), 11, 31);
    } else if (period === 'since2020') {
        // 2020'den Beri: 01.01.2020 - 31.12.bugünYılı
        startDate = new Date(2020, 0, 1);
        endDate = new Date(today.getFullYear(), 11, 31);
    }

    const formatDate = (d) => {
        const day = String(d.getDate()).padStart(2, '0');
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const year = d.getFullYear();
        return `${day}.${month}.${year}`;
    };

    const parseDate = (dateStr) => {
        const [day, month, year] = dateStr.split('.');
        return new Date(year, month - 1, day);
    };

    const startStr = formatDate(startDate);
    const endStr = formatDate(endDate);

    console.log(`🔍 Filter: ${period} | Tarih Aralığı: ${startStr} - ${endStr}`);
    console.log(`📊 Toplam kayıt: ${allData.length}`);

    // Tarih aralığına göre filtrele
    globalModalData = allData.filter(record => {
        if (!record.Tarih || record.Sıra <= 0) return false;
        const recordDate = parseDate(record.Tarih);
        return recordDate >= startDate && recordDate <= endDate;
    });

    console.log(`✅ Filtrelenen kayıt: ${globalModalData.length}`);

    if (globalModalData.length === 0) {
        console.warn(`⚠️ Seçilen tarih aralığında kayıt yok: ${startStr} - ${endStr}`);
        // Boş veri ile de modal aç, ama "Veri bulunamadı" mesajı göster
    }

    // Modal aç
    const monthNames = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'];
    const currentMonthName = monthNames[today.getMonth()];
    const year = today.getFullYear();
    const labels = {
        'currentMonth': `Bu Ay (${currentMonthName} ${year})`,
        'currentYear': `Bu Yıl (01.01.${year} - 31.12.${year})`,
        'last3Years': `Son 3 Yıl (01.01.${year-2} - 31.12.${year})`,
        'since2020': `2020'den Beri (01.01.2020 - 31.12.${year})`
    };

    // TARIH ARILIGI: 2 sayfa modal aç
    openRangeModal2Pages(globalModalData, labels[period], period);
}

// ===== FILTER BY SELECTED DATE =====
function filterBySelectedDate() {
    if (!databaseReady) {
        setTimeout(filterBySelectedDate, 100);
        return;
    }
    const selectedDateInput = document.getElementById('selectedDate');
    if (!selectedDateInput || !selectedDateInput.value) {
        alert('Lütfen bir tarih seçin');
        return;
    }
    // selectedDate format: YYYY-MM-DD
    const [year, month, day] = selectedDateInput.value.split('-');
    const filterDate = `${String(day).padStart(2, '0')}.${String(month).padStart(2, '0')}.${year}`;
    console.log(`🔍 Seçilen tarih: ${filterDate}`);
    console.log(`📊 Toplam kayıt: ${allData.length}`);
    const filtered = allData.filter(record => record.Tarih === filterDate);
    console.log(`✅ Filtrelenen kayıt: ${filtered.length}`);
    if (filtered.length === 0) {
        alert(`${filterDate} tarihinde kayıt bulunamadı`);
        return;
    }
    // Farklı turnuva isimlerini bul
    const uniqueTournaments = [...new Set(filtered.map(r => r.Turnuva || ''))];
    if (uniqueTournaments.length > 1) {
        // Kullanıcıya seçim sun
        showTournamentSelectModal(uniqueTournaments, function(selectedTournament) {
            const tournamentData = filtered.filter(r => (r.Turnuva || '') === selectedTournament);
            openGlobalStatsModal(tournamentData, `Seçilen Tarih: ${filterDate} - ${selectedTournament}`);
        });
    } else {
        openGlobalStatsModal(filtered, `Seçilen Tarih: ${filterDate}${uniqueTournaments[0] ? ' - ' + uniqueTournaments[0] : ''}`);
    }
// Turnuva seçimi modalı fonksiyonları
function showTournamentSelectModal(tournamentList, onSelect) {
    const modal = document.getElementById('tournamentSelectModal');
    const listDiv = document.getElementById('tournamentSelectList');
    listDiv.innerHTML = '';
    tournamentList.forEach(name => {
        const btn = document.createElement('button');
        btn.textContent = name || '(isimsiz)';
        btn.style = 'display:block;width:100%;margin-bottom:10px;padding:10px 0;background:#ff9800;color:#fff;font-weight:bold;border:none;border-radius:8px;cursor:pointer;font-size:1em;';
        btn.onclick = () => {
            modal.style.display = 'none';
            if (onSelect) onSelect(name);
        };
        listDiv.appendChild(btn);
    });
    modal.style.display = 'flex';
}

function closeTournamentSelectModal() {
    document.getElementById('tournamentSelectModal').style.display = 'none';
}
}

// ===== GLOBAL RANGE MODAL (2-Sayfa: Şampiyonlar + Sonuçlar) =====
function openGlobalRangeModal(data, filterLabel) {
    if (!databaseReady || !data) {
        console.warn('Database not ready or no data');
        return;
    }
    
    // Use global variable for consistency
    window.globalRangeData = data;
    window.globalRangeData = data;
    window.currentRangeTab = 1;
    
    // Remove old modal if exists
    let modal = document.getElementById('globalRangeModal');
    if (modal) modal.remove();
    
    // Create modal dynamically - this ensures no CSS conflicts
    modal = document.createElement('div');
    modal.id = 'globalRangeModal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        z-index: 99999;
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        display: flex;
        align-items: center;
        justify-content: center;
    `;
    
    // Inner white container
    const innerDiv = document.createElement('div');
    innerDiv.style.cssText = `
        width: 90%;
        height: 90%;
        max-width: 1200px;
        background: white;
        border-radius: 8px;
        display: flex;
        flex-direction: column;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    `;
    
    // Header
    const header = document.createElement('div');
    header.style.cssText = `
        padding: 15px 20px;
        background: #1e3c72;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-shrink: 0;
        border-radius: 8px 8px 0 0;
    `;
    
    const title = document.createElement('h2');
    title.id = 'rangeModalTitle';
    title.textContent = filterLabel || '📊 Turnuva Analizi';
    title.style.cssText = `
        margin: 0;
        font-size: 1.3em;
        flex: 1;
        text-align: center;
    `;
    
    const closeBtn = document.createElement('button');
    closeBtn.textContent = '✕';
    closeBtn.onclick = closeGlobalRangeModal;
    closeBtn.style.cssText = `
        background: none;
        border: none;
        color: white;
        font-size: 1.5em;
        cursor: pointer;
        padding: 0;
        width: 30px;
        height: 30px;
        flex-shrink: 0;
    `;
    
    header.appendChild(title);
    header.appendChild(closeBtn);
    
    // Content area
    const contentArea = document.createElement('div');
    contentArea.id = 'rangeModalContent';
    contentArea.style.cssText = `
        flex: 1;
        overflow-y: auto;
        padding: 20px;
        background: white;
    `;
    
    // Navigation buttons
    const navDiv = document.createElement('div');
    navDiv.style.cssText = `
        padding: 12px;
        background: #f8f9fa;
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 10px;
        flex-shrink: 0;
        border-bottom: 1px solid #e0e0e0;
    `;
    
    const prevBtn = document.createElement('button');
    prevBtn.id = 'rangePrevBtn';
    prevBtn.textContent = '← Önceki';
    prevBtn.onclick = () => showGlobalRangeTab(window.currentRangeTab - 1);
    prevBtn.style.cssText = `
        padding: 8px 15px;
        background: #667eea;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-weight: bold;
    `;
    
    const spacer = document.createElement('div');
    spacer.style.flex = '1';
    
    const nextBtn = document.createElement('button');
    nextBtn.id = 'rangeNextBtn';
    nextBtn.textContent = 'Sonraki →';
    nextBtn.onclick = () => showGlobalRangeTab(window.currentRangeTab + 1);
    nextBtn.style.cssText = `
        padding: 8px 15px;
        background: #667eea;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-weight: bold;
    `;
    
    navDiv.appendChild(prevBtn);
    navDiv.appendChild(spacer);
    navDiv.appendChild(nextBtn);
    
    // Page indicator
    const pageDiv = document.createElement('div');
    pageDiv.style.cssText = `
        padding: 10px;
        background: #f8f9fa;
        text-align: center;
        flex-shrink: 0;
        border-radius: 0 0 8px 8px;
    `;
    
    const pageIndicator = document.createElement('span');
    pageIndicator.id = 'rangePageIndicator';
    pageIndicator.textContent = 'Sayfa 1/2';
    pageIndicator.style.cssText = `
        font-weight: bold;
        color: #667eea;
        font-size: 0.95em;
    `;
    
    pageDiv.appendChild(pageIndicator);
    
    // Assemble
    innerDiv.appendChild(header);
    innerDiv.appendChild(contentArea);
    innerDiv.appendChild(navDiv);
    innerDiv.appendChild(pageDiv);
    
    modal.appendChild(innerDiv);
    document.body.appendChild(modal);
    
    document.body.style.overflow = 'hidden';
    
    console.log('✅ Dynamic modal created and displayed');
    
    // Render first page
    showGlobalRangeTab(1);
    console.log('✓ Global Range Modal açıldı:', data.length, 'kayıt');
}

function closeGlobalRangeModal() {
    const modal = document.getElementById('globalRangeModal');
    if (modal) {
        modal.remove();
        document.body.style.overflow = 'auto';
    }
}

function showGlobalRangeTab(tabNum) {
    try {
        // Boundary check
        if (tabNum < 1) tabNum = 1;
        if (tabNum > 2) tabNum = 2;
        
        window.currentRangeTab = tabNum;
        
        const data = window.globalRangeData || [];
        const contentArea = document.getElementById('rangeModalContent');
        const pageIndicator = document.getElementById('rangePageIndicator');
        const prevBtn = document.getElementById('rangePrevBtn');
        const nextBtn = document.getElementById('rangeNextBtn');
        const title = document.getElementById('rangeModalTitle');
        
        console.log(`📄 showGlobalRangeTab(${tabNum}):`, {
            dataLength: data.length,
            contentAreaFound: !!contentArea,
            titleFound: !!title
        });
        
        if (!contentArea) {
            console.error('rangeModalContent not found');
            return;
        }
    
    // Update page indicator
    if (pageIndicator) pageIndicator.textContent = `Sayfa ${tabNum}/2`;
    
    // Update button visibility
    if (prevBtn) prevBtn.style.visibility = tabNum > 1 ? 'visible' : 'hidden';
    if (nextBtn) nextBtn.style.visibility = tabNum < 2 ? 'visible' : 'hidden';
    
    if (tabNum === 1) {
        // Sayfa 1: İstatistikler (Top 3 1.lik + Top 3 Skor Ortalaması)
        console.log('📄 Tab 1 başladı');
        if (title) title.textContent = '📊 İstatistikler';
        
        // Top 3 En Çok 1.lik Kazananlar
        const firstPlaceStats = {};
        data.forEach(row => {
            if (parseInt(row['Sıra']) === 1) {
                const p1 = normalizeText(row['Oyuncu 1'].trim());
                const p2 = normalizeText(row['Oyuncu 2'].trim());
                firstPlaceStats[p1] = (firstPlaceStats[p1] || 0) + 1;
                firstPlaceStats[p2] = (firstPlaceStats[p2] || 0) + 1;
            }
        });
        
        const topFirstPlace = Object.entries(firstPlaceStats)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 3);
        
        console.log('📊 topFirstPlace:', topFirstPlace.length);
        // Top 3 Skor Ortalaması En Yüksek
        const playerScores = {};
        data.forEach(row => {
            const p1 = normalizeText(row['Oyuncu 1'].trim());
            const p2 = normalizeText(row['Oyuncu 2'].trim());
            const score = parseFloat(row['Skor']) || 0;
            
            if (!playerScores[p1]) playerScores[p1] = { total: 0, count: 0 };
            if (!playerScores[p2]) playerScores[p2] = { total: 0, count: 0 };
            
            playerScores[p1].total += score;
            playerScores[p1].count += 1;
            playerScores[p2].total += score;
            playerScores[p2].count += 1;
        });
        
        const topAvgScore = Object.entries(playerScores)
            .map(([name, stats]) => ({name, avg: (stats.total / stats.count).toFixed(2)}))
            .sort((a, b) => parseFloat(b.avg) - parseFloat(a.avg))
            .slice(0, 3);
        
        let html = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:15px;">';
        
        // Top 3 1.lik Kazananlar
        html += '<div style="background:#fff5e6;border-radius:8px;padding:15px;">';
        html += '<div style="color:#d97706;font-weight:bold;font-size:0.95em;text-align:center;margin-bottom:12px;">🏆 En Çok 1.lik Kazananlar</div>';
        
        if (topFirstPlace.length === 0) {
            html += '<div style="color:#999;text-align:center;padding:20px;">Veri yok</div>';
        } else {
            html += '<div style="display:flex;flex-direction:column;gap:8px;">';
            topFirstPlace.forEach((item, idx) => {
                html += '<div style="background:white;padding:10px;border-radius:6px;border-left:3px solid #d97706;">';
                html += `<div style="display:flex;justify-content:space-between;align-items:center;">`;
                html += `<div style="font-weight:bold;color:#1e3c72;font-size:0.85em;">${idx+1}. ${item[0]}</div>`;
                html += `<div style="background:#fef3c7;color:#d97706;font-weight:bold;padding:4px 8px;border-radius:4px;font-size:0.8em;">${item[1]} ×</div>`;
                html += '</div></div>';
            });
            html += '</div>';
        }
        html += '</div>';
        
        // Top 3 Skor Ortalaması
        html += '<div style="background:#f0fdf4;border-radius:8px;padding:15px;">';
        html += '<div style="color:#16a34a;font-weight:bold;font-size:0.95em;text-align:center;margin-bottom:12px;">📈 Skor Ortalaması En Yüksek</div>';
        
        if (topAvgScore.length === 0) {
            html += '<div style="color:#999;text-align:center;padding:20px;">Veri yok</div>';
        } else {
            html += '<div style="display:flex;flex-direction:column;gap:8px;">';
            topAvgScore.forEach((item, idx) => {
                html += '<div style="background:white;padding:10px;border-radius:6px;border-left:3px solid #16a34a;">';
                html += `<div style="display:flex;justify-content:space-between;align-items:center;">`;
                html += `<div style="font-weight:bold;color:#1e3c72;font-size:0.85em;">${idx+1}. ${item.name}</div>`;
                html += `<div style="background:#dcfce7;color:#16a34a;font-weight:bold;padding:4px 8px;border-radius:4px;font-size:0.8em;">% ${item.avg}</div>`;
                html += '</div></div>';
            });
            html += '</div>';
        }
        html += '</div></div>';
        
        console.log('📄 Tab 1 HTML uzunluğu:', html.length);
        contentArea.innerHTML = html;
        console.log('✅ Tab 1 HTML set edildi');
        
    } else if (tabNum === 2) {
        // Sayfa 2: Turnuva Sonuçları (Tarih | NS-1 | Oyuncu 1 | Oyuncu 2 | % Skor)
        if (title) title.textContent = '🎯 Turnuva Sonuçları';
        
        // Excel'e aktar fonksiyonu
        const exportToExcel = () => {
            try {
                const sorted = [...data].sort((a, b) => {
                    const dateA = a['Tarih'].split('.').reverse().join('-');
                    const dateB = b['Tarih'].split('.').reverse().join('-');
                    return dateB.localeCompare(dateA);
                });
                
                let csv = 'Tarih\tSıra\tOyuncu 1\tOyuncu 2\tSkor\n';
                sorted.forEach(row => {
                    const tarihParts = row['Tarih'].split('.');
                    const tarihFormat = tarihParts[0] + '.' + tarihParts[1] + '.' + (tarihParts[2].length > 2 ? tarihParts[2].slice(-2) : tarihParts[2]);
                    csv += `${tarihFormat}\t${row['Sıra']}\t${row['Oyuncu 1']}\t${row['Oyuncu 2']}\t${row['Skor']}\n`;
                });
                
                const blob = new Blob([csv], {type: 'text/plain'});
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'turnuva_sonuclari.txt';
                a.click();
                URL.revokeObjectURL(url);
                alert('✅ Veriler indirildi! Excel\'e yapıştırabilirsiniz.');
            } catch (e) {
                alert('Hata: ' + e.message);
            }
        };
        
        // Verileri tarihine göre sırala (eskiden yeniye)
        const sorted = [...data].sort((a, b) => {
            const dateA = a['Tarih'].split('.').reverse().join('-');
            const dateB = b['Tarih'].split('.').reverse().join('-');
            return dateB.localeCompare(dateA);
        });
        
        let html = '<div style="display:flex;flex-direction:column;gap:12px;">';
        
        // Excel Export Butonu
        html += '<button onclick="window.exportGlobalResults()" style="padding:10px;background:#10b981;color:white;border:none;border-radius:6px;font-weight:bold;cursor:pointer;margin-bottom:8px;">📥 Excel\'e Aktar</button>';
        
        // Başlık
        html += '<div style="display:grid;grid-template-columns:80px 60px 1fr 1fr 80px;gap:10px;padding:12px;background:#667eea;color:white;border-radius:8px;font-weight:bold;font-size:0.85em;position:sticky;top:0;z-index:10;">';
        html += '<div style="text-align:center;">📅 Tarih</div>';
        html += '<div style="text-align:center;">🎯 Sıra</div>';
        html += '<div style="text-align:center;">👤 Oyuncu 1</div>';
        html += '<div style="text-align:center;">👤 Oyuncu 2</div>';
        html += '<div style="text-align:center;">📊 Skor</div>';
        html += '</div>';
        
        // Satırlar
        if (sorted.length === 0) {
            html += '<div style="text-align:center;color:#999;padding:20px;">Sonuç bulunamadı</div>';
        } else {
            sorted.forEach(row => {
                const tarihParts = row['Tarih'].split('.');
                const tarihFormat = tarihParts[0] + '.' + tarihParts[1] + '.' + (tarihParts[2].length > 2 ? tarihParts[2].slice(-2) : tarihParts[2]);
                const score = parseFloat(row['Skor']) || 0;
                const scoreColor = score >= 50 ? '#16a34a' : '#dc2626';
                
                html += '<div style="display:grid;grid-template-columns:80px 60px 1fr 1fr 80px;gap:10px;padding:12px;background:white;border:1px solid #e5e7eb;border-radius:6px;align-items:center;">';
                html += `<div style="text-align:center;font-weight:600;color:#1e3c72;font-size:0.85em;">${tarihFormat}</div>`;
                html += `<div style="text-align:center;font-weight:600;color:#667eea;font-size:0.85em;">${row['Sıra']}</div>`;
                html += `<div style="text-align:center;color:#374151;font-weight:500;font-size:0.85em;">${row['Oyuncu 1']}</div>`;
                html += `<div style="text-align:center;color:#374151;font-weight:500;font-size:0.85em;">${row['Oyuncu 2']}</div>`;
                html += `<div style="text-align:center;font-weight:bold;color:${scoreColor};font-size:0.85em;">% ${score.toFixed(2)}</div>`;
                html += '</div>';
            });
        }
        
        html += '</div>';
        contentArea.innerHTML = html;
        
        // Export fonksiyonunu window'a bağla
        window.exportGlobalResults = exportToExcel;
    }
    } catch (error) {
        console.error('❌ showGlobalRangeTab error:', error);
    }
}

// ===== MODAL OPENING =====
function openGlobalStatsModal(data, filterLabel) {
    // BELİRLİ TARIH: 3 sayfa modal aç
    window.dailyModalData = data;
    showMobileModal(data);
}

// ===== MODAL CLOSING =====
function closeGlobalStatsModal() {
    const modal = document.getElementById('globalStatsModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// ===== PAGE INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function() {
    console.log('✓ DOM yüklendi - Dil sistemi başlatılıyor...');
    
    // Dil sistemini başlat
    initLanguage().then(() => {
        console.log(`✓ Dil sistemi hazır (${currentLanguage.toUpperCase()})`);
    });
    
    // Sayfa yenilendiğinde ana modal kapalı olmalı
    const globalStatsModal = document.getElementById('globalStatsModal');
    if (globalStatsModal) {
        globalStatsModal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
    console.log('✓ DOM yüklendi');

    const modal = document.getElementById('globalStatsModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) closeGlobalStatsModal();
        });
    }

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') closeGlobalStatsModal();
    });

    // Auto-copy temp database if main is empty or invalid
    // Use Flask endpoints for database loading
    function tryLoadDatabase(mainFile, fallbackFile) {
        let mainUrl = './database.json?v=' + Date.now();
        let fallbackUrl = './database_temp.json?v=' + Date.now();
        fetch(mainUrl)
            .then(response => {
                if (!response.ok) throw new Error('Veritabanı yüklenemedi');
                return response.json();
            })
            .then(data => {
                if (!Array.isArray(data) || data.length === 0) {
                    if (fallbackFile) {
                        document.getElementById('fileInfo').innerHTML = '<span style="color:orange;">⚠️ Veritabanı boş, yedek yükleniyor...</span>';
                        fetch(fallbackUrl)
                            .then(r => r.json())
                            .then(fallbackData => {
                                if (Array.isArray(fallbackData) && fallbackData.length > 0) {
                                    allData = fallbackData;
                                    updateFileInfo();
                                    databaseReady = true;
                                    initializePlayerSearch();
                                    if (queuedModalOpen) {
                                        openGlobalStatsModal(...queuedModalOpen);
                                        queuedModalOpen = null;
                                    }
                                } else {
                                    document.getElementById('fileInfo').innerHTML = '<span style="color:red;">❌ Hiçbir veritabanı yüklenemedi. Lütfen database.json veya database_temp.json dosyasını kontrol edin.</span>';
                                    allData = [];
                                    databaseReady = false;
                                }
                            })
                            .catch(() => {
                                document.getElementById('fileInfo').innerHTML = '<span style="color:red;">❌ Hiçbir veritabanı yüklenemedi. Lütfen database.json veya database_temp.json dosyasını kontrol edin.</span>';
                                allData = [];
                                databaseReady = false;
                            });
                        return;
                    } else {
                        document.getElementById('fileInfo').innerHTML = '<span style="color:red;">❌ Hiçbir veritabanı yüklenemedi. Lütfen database.json veya database_temp.json dosyasını kontrol edin.</span>';
                        allData = [];
                        databaseReady = false;
                        return;
                    }
                } else {
                    allData = data;
                    updateFileInfo();
                    databaseReady = true;
                    initializePlayerSearch();
                    // If a modal open was queued, run it now
                    if (queuedModalOpen) {
                        openGlobalStatsModal(...queuedModalOpen);
                        queuedModalOpen = null;
                    }
                }
            })
            .catch(err => {
                document.getElementById('fileInfo').innerHTML = `<span style='color:red;'>❌ Hiçbir veritabanı yüklenemedi: ${err.message}</span>`;
                allData = [];
                databaseReady = false;
            });
    }
    tryLoadDatabase('database.json', 'database_temp.json');
});

// ===== MODAL NAVIGATION HANDLERS =====
function handleModalPrevClick() {
    // 2-page modal mı yoksa 3-page modal mı kontrol et
    const pageEl = document.getElementById('currentPage');
    const pageText = pageEl ? pageEl.textContent : '1/3';
    
    if (pageText.includes('/2')) {
        // 2-page modal (tarih aralığı)
        const newTab = (window.currentRangeTab || 1) - 1;
        show2PageTab(newTab);
    } else {
        // 3-page modal (belirli tarih)
        const newTab = (window.currentDailyTab || 1) - 1;
        showDailyResultTab(newTab);
    }
}

function handleModalNextClick() {
    // 2-page modal mı yoksa 3-page modal mı kontrol et
    const pageEl = document.getElementById('currentPage');
    const pageText = pageEl ? pageEl.textContent : '1/3';
    
    if (pageText.includes('/2')) {
        // 2-page modal (tarih aralığı)
        const newTab = (window.currentRangeTab || 1) + 1;
        show2PageTab(newTab);
    } else {
        // 3-page modal (belirli tarih)
        const newTab = (window.currentDailyTab || 1) + 1;
        showDailyResultTab(newTab);
    }
}

function normalizePlayerName(name) {
    // Türkçe karakterleri dikkate al: İ→i, ş→ş, ğ→ğ vb
    if (!name) return '';
    const turkishMap = {
        'İ': 'i', 'I': 'ı', 'Ş': 'ş', 'Ğ': 'ğ', 'Ü': 'ü', 'Ö': 'ö', 'Ç': 'ç'
    };
    let lower = '';
    for (let char of name) {
        lower += turkishMap[char] || char.toLowerCase();
    }
    return lower
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

function parseDate(dateStr) {
    // "29.12.24" → Date object
    if (!dateStr) return new Date(0);
    const [day, month, year] = dateStr.split('.');
    const fullYear = year.length === 2 ? '20' + year : year;
    return new Date(fullYear, month - 1, day);
}

function openRangeModal2Pages(data, filterLabel, period) {
    console.log('🔔 openRangeModal2Pages çağrıldı:', data.length, 'kayıt, Period:', period);
    
    if (!data || data.length === 0) {
        data = [];
    }
    
    window.currentRangeTab = 1;
    window.rangeModalData = data;
    window.rangePeriod = period;  // Period'u kaydet - istatistik hesaplaması için
    
    // Modal öğesi
    const modal = document.getElementById('mobileResultsModal');
    if (!modal) {
        console.error('❌ mobileResultsModal element bulunamadı!');
        return;
    }
    
    // Header
    const header = document.getElementById('modalHeaderLabel');
    if (header) {
        header.textContent = filterLabel || '📊 Turnuva Analizi';
    }
    
    // Page counter: 2 sayfa
    const currentPageEl = document.getElementById('currentPage');
    if (currentPageEl) {
        currentPageEl.innerHTML = '<span id="rangePage">1</span>/2';
    }
    
    // Modal'ı aç
    modal.style.display = 'flex';
    modal.style.flexDirection = 'column';
    document.body.style.overflow = 'hidden';
    
    console.log('✓ mobileResultsModal açıldı (2 sayfa - Tarih Aralığı)');
    
    // İlk sayfayı göster
    show2PageTab(1);
}

function show2PageTab(tabNum) {
    // Sınırları kontrol et - 2 SAYFA
    if (tabNum < 1) tabNum = 1;
    if (tabNum > 2) tabNum = 2;
    
    window.currentRangeTab = tabNum;
    
    const data = window.rangeModalData || [];
    const contentArea = document.getElementById('dailyResultsContent');
    const pageEl = document.getElementById('currentPage');
    const header = document.getElementById('modalHeaderLabel');
    const prevBtn = document.getElementById('dailyPrevBtn');
    const nextBtn = document.getElementById('dailyNextBtn');
    
    // Update page indicator - /2 ile kapat (2-page modal)
    if (pageEl) {
        pageEl.textContent = tabNum + '/2';
    }
    
    // Butonların görünürlüğünü kontrol et
    // 2 SAYFA: Tab 1 = Önceki gizli, Sonraki görünür | Tab 2 = Önceki görünür, Sonraki gizli
    if (prevBtn) prevBtn.style.visibility = tabNum > 1 ? 'visible' : 'hidden';
    if (nextBtn) nextBtn.style.visibility = tabNum < 2 ? 'visible' : 'hidden';
    
    if (tabNum === 1) {
        // Tab 1: İSTATİSTİKLER (Top 3 1.lik + Top 3 Skor Ortalaması)
        if (header) header.textContent = getTranslation('rankings.statistics');
        console.log(`📄 Tab 1: İstatistikler ${data.length} veri satırı`);
        
        // Minimum turnuva kriteri
        const minTournaments = {
            'currentMonth': 3,
            'currentYear': 25,
            'last3Years': 50,
            'since2020': 50
        };
        const minRequired = minTournaments[window.rangePeriod] || 3;
        console.log(`🎯 Minimum turnuva kriteri: ${minRequired}`);
        
        // Top 3 En Çok 1.lik Kazananlar
        const firstPlaceStats = {};
        data.forEach(record => {
            if (record['Sıra'] === 1 || record['Sıra'] === '1') {
                const players = [record['Oyuncu 1'], record['Oyuncu 2']];
                players.forEach(player => {
                    if (player) {
                        const normalized = normalizeText(player);
                        if (!firstPlaceStats[normalized]) {
                            firstPlaceStats[normalized] = { name: player, count: 0 };
                        }
                        firstPlaceStats[normalized].count++;
                    }
                });
            }
        });
        
        const topFirstPlace = Object.values(firstPlaceStats)
            .sort((a, b) => b.count - a.count)
            .slice(0, 3);
        
        // Top 3 Skor Ortalaması En Yüksek (minimum turnuva kriteri ile)
        const playerScores = {};
        data.forEach(record => {
            const players = [record['Oyuncu 1'], record['Oyuncu 2']];
            players.forEach(player => {
                if (player) {
                    const normalized = normalizeText(player);
                    const score = parseFloat(record['Skor']) || 0;
                    if (!playerScores[normalized]) {
                        playerScores[normalized] = { name: player, total: 0, count: 0 };
                    }
                    playerScores[normalized].total += score;
                    playerScores[normalized].count++;
                }
            });
        });
        
        // Minimum kriteri sağlayanları filtrele
        const topAvgScores = Object.values(playerScores)
            .filter(p => p.count >= minRequired)  // Minimum turnuva kriteri
            .map(p => ({ ...p, average: p.total / p.count }))
            .sort((a, b) => b.average - a.average)
            .slice(0, 3);
        
        // ALT ALTA 2 CONTAINER - EŞİT ÖLÇÜDE, SAYFAYI KAPLASSIN
        let html = `<div style='display:flex;flex-direction:column;gap:0;height:100%;overflow:hidden;'>`;
        
        // Container 1: En Çok 1.lik Kazananlar (50%) - Turuncu tema
        html += `<div style='flex:1;display:flex;flex-direction:column;overflow-y:auto;padding:15px;background:#fef3c7;border-bottom:2px solid #fcd34d;'>`;
        html += `<div style='color:#92400e;font-weight:bold;font-size:1.1em;margin-bottom:10px;text-align:center;'>🏆 ${getTranslation('rankings.topChampions')}</div>`;
        topFirstPlace.forEach((player, idx) => {
            html += `<div style='padding:12px;margin-bottom:8px;background:#fcd34d;border-radius:6px;color:#1e3c72;font-weight:bold;display:flex;justify-content:flex-start;align-items:center;gap:15px;'>`;
            html += `<span style='min-width:30px;'>${idx + 1}</span>`;
            html += `<span>${normalizePlayerName(player.name)}</span>`;
            html += `<span style='margin-left:auto;'>${player.count} ${getTranslation('rankings.times')}</span>`;
            html += `</div>`;
        });
        html += `</div>`;
        
        // Container 2: Skor Ortalaması (50%) - Yeşil tema
        html += `<div style='flex:1;display:flex;flex-direction:column;overflow-y:auto;padding:15px;background:#dcfce7;'>`;
        html += `<div style='color:#15803d;font-weight:bold;font-size:1.1em;margin-bottom:10px;text-align:center;'>📈 ${getTranslation('rankings.scoreAverageMin').replace('{count}', minRequired)}</div>`;
        topAvgScores.forEach((player, idx) => {
            html += `<div style='padding:12px;margin-bottom:8px;background:#86efac;border-radius:6px;color:#1e3c72;font-weight:bold;display:flex;justify-content:flex-start;align-items:center;gap:15px;'>`;
            html += `<span style='min-width:30px;'>${idx + 1}</span>`;
            html += `<span>${normalizePlayerName(player.name)}</span>`;
            html += `<span style='margin-left:auto;'>% ${player.average.toFixed(2)}</span>`;
            html += `</div>`;
        });
        html += `</div>`;
        
        html += `</div>`;
        
        if (contentArea) {
            contentArea.innerHTML = html;
        }
        
    } else if (tabNum === 2) {
        // Tab 2: TURNUVA SONUÇLARI
        const titleMap = {
            'currentMonth': getTranslation('modal.monthResults'),
            'currentYear': getTranslation('modal.yearResults'),
            'last3Years': getTranslation('modal.last3YearsResults'),
            'since2020': getTranslation('modal.since2020Results')
        };
        const tabTitle = titleMap[window.rangePeriod] || getTranslation('modal.tournamentsAndResults');
        if (header) header.textContent = tabTitle;
        console.log(`📄 Tab 2: ${tabTitle} ${data.length} kayıt`);
        
        const sortedData = [...data].sort((a, b) => {
            const dateA = parseDate(a.Tarih);
            const dateB = parseDate(b.Tarih);
            return dateA - dateB;  // Eskiden yeniye doğru
        });
        
        // Tarih formatlama ve gün adı
        function formatDate(tarihStr) {
            const [day, month, year] = tarihStr.split('.');
            const fullYear = year.length === 2 ? '20' + year : year;
            const dateObj = new Date(fullYear, month - 1, day);
            const dayNames = ['Pazar', 'Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi'];
            const dayName = dayNames[dateObj.getDay()];
            const formattedDate = `${day.padStart(2, '0')}.${month.padStart(2, '0')}.${fullYear}`;
            return { full: formattedDate, dayName };
        }
        
        let html = `<div style='display:flex;flex-direction:column;gap:0;height:100%;overflow:hidden;'>`;
        
        // Excel butonu - Fosfor yeşili
        html += `<div style='padding:12px;background:#ffffff;border-bottom:2px solid #39ff14;'>`;
        html += `<button onclick='window.exportGlobalResults()' style='width:100%;padding:12px 15px;background:#39ff14;color:#000;border:none;border-radius:5px;cursor:pointer;font-weight:bold;font-size:0.95em;'>📥 Excel'e Aktar</button>`;
        html += `</div>`;
        
        // Sonuçlar - tarihe göre gruplandırılmış
        html += `<div style='flex:1;overflow-y:auto;display:flex;flex-direction:column;gap:0;padding:0;background:#f5f5f5;'>`;
        
        // Tarihlere göre grup
        const groupedByDate = {};
        sortedData.forEach(record => {
            const tarih = record.Tarih;
            if (!groupedByDate[tarih]) {
                groupedByDate[tarih] = [];
            }
            groupedByDate[tarih].push(record);
        });
        
        // Her tarih grubunu işle
        Object.keys(groupedByDate).forEach(tarih => {
            const { full: formattedDate, dayName } = formatDate(tarih);
            const records = groupedByDate[tarih];
            
            // Tarih başlığı - MAVİ
            html += `<div style='padding:10px;background:#1e3c72;color:#fff;font-weight:bold;font-size:0.9em;text-align:center;border-bottom:1px solid #0f2340;'>`;
            html += `${formattedDate} - ${dayName}`;
            html += `</div>`;
            
            // Direction'a göre grupla
            const byDirection = { 'NS': [], 'EW': [] };
            records.forEach(record => {
                const dir = record['Direction'] || (record.Sıra <= 12 ? 'NS' : 'EW');
                byDirection[dir].push(record);
            });
            
            // Kuzey-Güney (NS)
            if (byDirection['NS'].length > 0) {
                html += `<div style='padding:8px 10px;background:#e8f4f8;color:#1e3c72;font-weight:bold;font-size:0.85em;border-left:4px solid #1ca7c1;'>${getTranslation('results.northSouth')}</div>`;
                byDirection['NS'].forEach((record, idx) => {
                    const score = parseFloat(record.Skor) || 0;
                    const bgColor = idx % 2 === 0 ? '#ffffff' : '#f9f9f9';
                    html += `<div style='padding:10px;background:${bgColor};border-bottom:1px solid #e5e5e5;display:flex;justify-content:space-between;align-items:flex-start;gap:10px;font-size:0.85em;'>`;
                    html += `<div style='display:flex;gap:6px;flex:1;'>`;
                    html += `<span style='color:#1e3c72;font-weight:bold;flex-shrink:0;'>${record.Sıra} -</span>`;
                    html += `<span style='color:#1e3c72;font-weight:bold;word-wrap:break-word;overflow-wrap:break-word;'>${record['Oyuncu 1']} & ${record['Oyuncu 2']}</span>`;
                    html += `</div>`;
                    html += `<span style='color:#1e3c72;font-weight:bold;flex-shrink:0;'>${score.toFixed(2)}</span>`;
                    html += `</div>`;
                });
            }
            
            // Doğu-Batı (EW)
            if (byDirection['EW'].length > 0) {
                html += `<div style='padding:8px 10px;background:#f0f8f0;color:#1e3c72;font-weight:bold;font-size:0.85em;border-left:4px solid #6db66d;'>${getTranslation('results.eastWest')}</div>`;
                byDirection['EW'].forEach((record, idx) => {
                    const score = parseFloat(record.Skor) || 0;
                    const bgColor = idx % 2 === 0 ? '#ffffff' : '#f9f9f9';
                    html += `<div style='padding:10px;background:${bgColor};border-bottom:1px solid #e5e5e5;display:flex;justify-content:space-between;align-items:flex-start;gap:10px;font-size:0.85em;'>`;
                    html += `<div style='display:flex;gap:6px;flex:1;'>`;
                    html += `<span style='color:#1e3c72;font-weight:bold;flex-shrink:0;'>${record.Sıra} -</span>`;
                    html += `<span style='color:#1e3c72;font-weight:bold;word-wrap:break-word;overflow-wrap:break-word;'>${record['Oyuncu 1']} & ${record['Oyuncu 2']}</span>`;
                    html += `</div>`;
                    html += `<span style='color:#1e3c72;font-weight:bold;flex-shrink:0;'>${score.toFixed(2)}</span>`;
                    html += `</div>`;
                });
            }
        });
        
        html += `</div></div>`;
        
        if (contentArea) {
            contentArea.innerHTML = html;
        }
        
        // Excel fonksiyonunu set et
        window.exportGlobalResults = () => {
            try {
                const sorted = [...data].sort((a, b) => {
                    const dateA = a['Tarih'].split('.').reverse().join('-');
                    const dateB = b['Tarih'].split('.').reverse().join('-');
                    return dateB.localeCompare(dateA);
                });
                
                // XLSX formatında dışa aktar
                const worksheet = XLSX.utils.json_to_sheet(
                    sorted.map(row => ({
                        'Tarih': row['Tarih'],
                        'Sıra': row['Sıra'],
                        'Oyuncu 1': row['Oyuncu 1'],
                        'Oyuncu 2': row['Oyuncu 2'],
                        'Skor': row['Skor']
                    }))
                );
                
                const workbook = XLSX.utils.book_new();
                XLSX.utils.book_append_sheet(workbook, worksheet, 'Turnuva Sonuçları');
                XLSX.writeFile(workbook, 'turnuva_sonuclari.xlsx');
                
                alert('✅ Veriler indirildi! (turnuva_sonuclari.xlsx)');
            } catch (e) {
                alert('Hata: ' + e.message);
            }
        };
    }
}

// ===== MOBİL MODAL FONKSİYONLARI =====

function showMobileModal(data) {
    console.log('showMobileModal çağrıldı, veri:', data ? data.length : 'NULL');
    if (!data || data.length === 0) {
        console.warn('⚠️ showMobileModal: Veri boş!');
        // Yine devam et, boş modal göster
        data = [];
    }
    
    window.currentDailyTab = 1;
    window.dailyModalData = data;
    console.log('window.dailyModalData set:', data.length, 'satır');
    
    // Desktop bölümlerini gizle
    const statsSection = document.getElementById('statsSection');
    const directionSection = document.getElementById('directionResultsSection');
    const championsSection = document.getElementById('championsSection');
    
    if (statsSection) statsSection.style.display = 'none';
    if (directionSection) directionSection.style.display = 'none';
    if (championsSection) championsSection.style.display = 'none';
    
    // Modal'ı aç
    const modal = document.getElementById('mobileResultsModal');
    if (modal) {
        modal.style.display = 'flex';
        modal.style.flexDirection = 'column';
        document.body.style.overflow = 'hidden';
        initSwipeNavigation(); // Swipe'ı başlat
        console.log('✓ mobileResultsModal açıldı');
    } else {
        console.error('❌ mobileResultsModal element bulunamadı!');
    }
    
    // İlk sayfayı göster
    showDailyResultTab(1);
}

function showDailyResultTab(tabNum) {
    // Sınırları kontrol et
    if (tabNum < 1) tabNum = 1;
    if (tabNum > 3) tabNum = 3;
    
    window.currentDailyTab = tabNum;
    
    const data = window.dailyModalData || [];
    const contentArea = document.getElementById('dailyResultsContent');
    const currentPageEl = document.getElementById('currentPage');
    const header = document.getElementById('modalHeaderLabel');
    const prevBtn = document.getElementById('dailyPrevBtn');
    const nextBtn = document.getElementById('dailyNextBtn');
    
    // Debug log
    console.log(`📄 showDailyResultTab(${tabNum}):`, {
        dataLength: data.length,
        contentAreaFound: !!contentArea,
        headerFound: !!header
    });
    
    // Update page indicator
    if (currentPageEl) currentPageEl.textContent = tabNum;
    
    // Butonların görünürlüğünü kontrol et
    if (prevBtn) prevBtn.style.visibility = tabNum > 1 ? 'visible' : 'hidden';
    if (nextBtn) nextBtn.style.visibility = tabNum < 3 ? 'visible' : 'hidden';
    
    if (tabNum === 1) {
        // Tab 1: Şampiyonlar
        if (header) header.textContent = getTranslation('rankings.champsOfDay');
        
        const champions = data.filter(row => row['Sıra'] === 1 || row['Sıra'] === '1');
        
        // Aynı oyuncu çiftini bir kez göster (en yüksek skor ile)
        const uniqueChampions = [];
        const seen = {};
        
        champions.forEach(champ => {
            const key = `${champ['Oyuncu 1']}|${champ['Oyuncu 2']}|${champ['Direction']}`;
            if (!seen[key]) {
                seen[key] = true;
                uniqueChampions.push(champ);
            }
        });
        
        const nsChamps = uniqueChampions.filter(c => c['Direction'] === 'NS');
        const ewChamps = uniqueChampions.filter(c => c['Direction'] === 'EW');
        
        let html = `<div style='display:flex;flex-direction:column;gap:10px;max-height:100%;'>`;
        
        // Kuzey-Güney
        html += `<div style='flex:1;background:#eaf6fb;border-radius:8px;padding:10px;overflow-y:auto;display:flex;flex-direction:column;justify-content:center;gap:8px;'>`;
        html += `<div style='color:#1ca7c1;font-weight:bold;font-size:0.9em;text-align:center;'>${getTranslation('results.northSouth')}</div>`;
        if (nsChamps.length === 0) {
            html += `<div style='color:#999;text-align:center;'>${getTranslation('results.noData')}</div>`;
        } else {
            nsChamps.forEach(champ => {
                html += `<div style='padding:8px;background:white;border-radius:4px;text-align:center;'>`;
                html += `<div style='font-weight:bold;color:#1e3c72;font-size:0.78em;line-height:1.4;margin-bottom:6px;'>${champ['Oyuncu 1']}</div>`;
                html += `<div style='font-weight:bold;color:#1e3c72;font-size:0.78em;line-height:1.4;margin-bottom:6px;'>${champ['Oyuncu 2']}</div>`;
                html += `<div style='color:#1ca7c1;font-size:0.76em;font-weight:bold;'>% ${champ['Skor']}</div>`;
                html += `</div>`;
            });
        }
        html += `</div>`;
        
        // Doğu-Batı
        html += `<div style='flex:1;background:#f0faea;border-radius:8px;padding:10px;overflow-y:auto;display:flex;flex-direction:column;justify-content:center;gap:8px;'>`;
        html += `<div style='color:#6db66d;font-weight:bold;font-size:0.9em;text-align:center;'>${getTranslation('results.eastWest')}</div>`;
        if (ewChamps.length === 0) {
            html += `<div style='color:#999;text-align:center;'>${getTranslation('results.noData')}</div>`;
        } else {
            ewChamps.forEach(champ => {
                html += `<div style='padding:8px;background:white;border-radius:4px;text-align:center;'>`;
                html += `<div style='font-weight:bold;color:#1e3c72;font-size:0.78em;line-height:1.4;margin-bottom:6px;'>${champ['Oyuncu 1']}</div>`;
                html += `<div style='font-weight:bold;color:#1e3c72;font-size:0.78em;line-height:1.4;margin-bottom:6px;'>${champ['Oyuncu 2']}</div>`;
                html += `<div style='color:#6db66d;font-size:0.76em;font-weight:bold;'>% ${champ['Skor']}</div>`;
                html += `</div>`;
            });
        }
        html += `</div></div>`;
        
        if (contentArea) {
            contentArea.innerHTML = html;
        } else {
            console.error('❌ dailyResultsContent element bulunamadı!');
        }
        
    } else if (tabNum === 2) {
        // Tab 2: Kuzey-Güney Sonuçları
        if (header) header.textContent = getTranslation('results.northSouthResults');
        
        const nsResults = data.filter(row => row['Direction'] === 'NS').sort((a, b) => {
            const aRank = parseInt(a['Sıra']) || 999;
            const bRank = parseInt(b['Sıra']) || 999;
            return aRank - bRank;
        });
        
        let html = '';
        if (nsResults.length === 0) {
            html += `<div style='text-align:center;color:#999;'>${getTranslation('results.noResults')}</div>`;
        } else {
            html += `<div style='display:flex;flex-direction:column;gap:8px;'>`;
            nsResults.forEach(row => {
                html += `<div style='background:#eaf6fb;border-radius:8px;padding:10px;display:flex;align-items:center;gap:8px;'>`;
                html += `<div style='font-weight:bold;color:#1e3c72;min-width:40px;text-align:center;background:white;padding:6px;border-radius:4px;font-size:0.9em;'>${row['Sıra']}</div>`;
                html += `<div style='flex:1;'>`;
                html += `<div style='font-weight:bold;color:#1e3c72;font-size:0.85em;'>${row['Oyuncu 1']} - ${row['Oyuncu 2']}</div>`;
                html += `<div style='color:#1ca7c1;font-size:0.75em;font-weight:bold;'>% ${row['Skor']}</div>`;
                html += `</div></div>`;
            });
            html += `</div>`;
        }
        if (contentArea) {
            contentArea.innerHTML = html;
        } else {
            console.error('❌ dailyResultsContent element bulunamadı!');
        }
        
    } else if (tabNum === 3) {
        // Tab 3: Doğu-Batı Sonuçları
        if (header) header.textContent = getTranslation('results.eastWestResults');
        
        const ewResults = data.filter(row => row['Direction'] === 'EW').sort((a, b) => {
            const aRank = parseInt(a['Sıra']) || 999;
            const bRank = parseInt(b['Sıra']) || 999;
            return aRank - bRank;
        });
        
        let html = '';
        if (ewResults.length === 0) {
            html += `<div style='text-align:center;color:#999;'>${getTranslation('results.noResults')}</div>`;
        } else {
            html += `<div style='display:flex;flex-direction:column;gap:8px;'>`;
            ewResults.forEach(row => {
                html += `<div style='background:#f0faea;border-radius:8px;padding:10px;display:flex;align-items:center;gap:8px;'>`;
                html += `<div style='font-weight:bold;color:#1e3c72;min-width:40px;text-align:center;background:white;padding:6px;border-radius:4px;font-size:0.9em;'>${row['Sıra']}</div>`;
                html += `<div style='flex:1;'>`;
                html += `<div style='font-weight:bold;color:#1e3c72;font-size:0.85em;'>${row['Oyuncu 1']} - ${row['Oyuncu 2']}</div>`;
                html += `<div style='color:#6db66d;font-size:0.75em;font-weight:bold;'>% ${row['Skor']}</div>`;
                html += `</div></div>`;
            });
            html += `</div>`;
        }
        if (contentArea) {
            contentArea.innerHTML = html;
        } else {
            console.error('❌ dailyResultsContent element bulunamadı!');
        }
    }
}

// ===== OYUNCU PERFORMANS MODAL FONKSIYONLARI =====
function openPlayerModal(playerName, data, period) {
    window.currentPlayerName = playerName;
    window.playerModalData = data;
    window.currentPlayerTab = 1;
    window.playerSortConfig = { sortBy: null, order: 'asc' };
    
    console.log('openPlayerModal çağırıldı:', { playerName, dataLength: data.length });
    
    const modal = document.getElementById('playerModal');
    if (!modal) {
        console.error('playerModal elementi bulunamadı!');
        return;
    }
    
    console.log('Modal element bulundu, açılıyor...');
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
    
    showPlayerTab(1);
}

function closePlayerModal() {
    const modal = document.getElementById('playerModal');
    if (modal) {
        modal.style.display = 'none';
    }
    document.body.style.overflow = 'auto';
    window.playerModalData = null;
}

function showPlayerTab(tabNum) {
    console.log('showPlayerTab çağırıldı:', tabNum);
    
    // Sınırları kontrol et
    if (tabNum < 1) tabNum = 1;
    if (tabNum > 2) tabNum = 2;
    
    const data = window.playerModalData || [];
    const playerName = window.currentPlayerName || '';
    const content = document.getElementById('playerModalContent');
    const title = document.getElementById('playerModalTitle');
    const pageIndicator = document.getElementById('playerPageIndicator');
    const prevBtn = document.getElementById('playerPrevBtn');
    const nextBtn = document.getElementById('playerNextBtn');
    
    console.log('Elementler kontrol ediliyor:', { 
        content: !!content, 
        title: !!title, 
        pageIndicator: !!pageIndicator,
        prevBtn: !!prevBtn,
        nextBtn: !!nextBtn
    });
    
    window.currentPlayerTab = tabNum;
    if (pageIndicator) pageIndicator.style.display = 'inline-block';
    if (pageIndicator) pageIndicator.textContent = `Sayfa ${tabNum}/2`;
    if (prevBtn) {
        prevBtn.style.display = tabNum > 1 ? 'block' : 'none';
    }
    if (nextBtn) {
        nextBtn.style.display = tabNum < 2 ? 'block' : 'none';
    }
    
    if (tabNum === 1) {
        // İstatistikler sayfası
        if (title) title.textContent = getTranslation('modal.playerStatistics');
        
        // Oynanma sayısı
        const playCount = data.length;
        
        // Kaç kez 1. olduğu
        const firstPlaceCount = data.filter(r => r['Sıra'] === 1 || r['Sıra'] === '1').length;
        
        // Partner bilgileri
        const partnerCount = {};
        const partnerBestScore = {};
        
        data.forEach(record => {
            // Partner bulurken normalize et (Türkçe karakterleri de)
            const oyuncu1Norm = normalizeText(record['Oyuncu 1'].trim().replace(/\s+/g, ' '));
            const oyuncu2Norm = normalizeText(record['Oyuncu 2'].trim().replace(/\s+/g, ' '));
            const partner = oyuncu1Norm === playerName ? record['Oyuncu 2'] : record['Oyuncu 1'];
            const score = parseFloat(record['Skor']) || 0;
            
            partnerCount[partner] = (partnerCount[partner] || 0) + 1;
            
            if (!partnerBestScore[partner] || score > partnerBestScore[partner].score) {
                partnerBestScore[partner] = { score: score, date: record['Tarih'] };
            }
        });
        
        const topPartner = Object.entries(partnerCount).sort((a, b) => b[1] - a[1])[0];
        const bestPartner = Object.entries(partnerBestScore).sort((a, b) => b[1].score - a[1].score)[0];
        
        // Skor ortalaması
        const totalScore = data.reduce((sum, r) => sum + (parseFloat(r['Skor']) || 0), 0);
        const avgScore = (totalScore / data.length).toFixed(2);
        
        // Farklı partner sayısı
        const uniquePartners = Object.keys(partnerCount).length;
        
        // Grid: 2x2 for bigger screens, responsive for smaller
        let html = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:20px;">';
        html += '<div style="background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);border-radius:8px;padding:12px;color:white;display:flex;flex-direction:column;justify-content:center;align-items:center;min-height:100px;">';
        html += '<div style="font-size:0.7em;opacity:0.9;margin-bottom:6px;text-align:center;">' + getTranslation('modal.tournamentsPlayed') + '</div>';
        html += '<div style="font-size:1.4em;font-weight:bold;line-height:1;">' + playCount + '</div></div>';
        
        html += '<div style="background:linear-gradient(135deg, #f093fb 0%, #f5576c 100%);border-radius:8px;padding:12px;color:white;display:flex;flex-direction:column;justify-content:center;align-items:center;min-height:100px;">';
        html += '<div style="font-size:0.7em;opacity:0.9;margin-bottom:6px;text-align:center;">' + getTranslation('modal.firstPlaceCount') + '</div>';
        html += '<div style="font-size:1.4em;font-weight:bold;line-height:1;">' + firstPlaceCount + '</div></div>';
        
        html += '<div style="background:linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);border-radius:8px;padding:12px;color:white;display:flex;flex-direction:column;justify-content:center;align-items:center;min-height:100px;">';
        html += '<div style="font-size:0.7em;opacity:0.9;margin-bottom:6px;text-align:center;">' + getTranslation('rankings.scoreAverage') + '</div>';
        html += '<div style="font-size:1.4em;font-weight:bold;line-height:1;">% ' + avgScore + '</div></div>';
        
        html += '<div style="background:linear-gradient(135deg, #1e8449 0%, #155724 100%);border-radius:8px;padding:12px;color:white;display:flex;flex-direction:column;justify-content:center;align-items:center;min-height:100px;">';
        html += '<div style="font-size:0.7em;opacity:0.9;margin-bottom:6px;text-align:center;">' + getTranslation('modal.differentPartnersCount') + '</div>';
        html += '<div style="font-size:1.4em;font-weight:bold;line-height:1;">' + uniquePartners + '</div></div>';
        html += '</div>';
        
        // Partner info section
        html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">';
        
        html += '<div style="background:#f8f9ff;border:2px solid #667eea;border-radius:8px;padding:12px;display:flex;flex-direction:column;justify-content:center;align-items:center;min-height:110px;text-align:center;">';
        html += '<div style="font-size:0.8em;color:#666;margin-bottom:8px;font-weight:bold;">' + getTranslation('modal.mostPlayedPartner') + '</div>';
        html += '<div style="font-size:1.1em;font-weight:bold;color:#1e3c72;margin-bottom:6px;word-break:break-word;">' + (topPartner ? topPartner[0] : 'N/A') + '</div>';
        html += '<div style="background:#667eea;color:white;padding:6px 10px;border-radius:4px;text-align:center;font-weight:bold;font-size:0.85em;width:100%;">' + (topPartner ? topPartner[1] + ' ' + getTranslation('rankings.times') : '-') + '</div>';
        html += '</div>';
        
        html += '<div style="background:#fff8f9;border:2px solid #f5576c;border-radius:8px;padding:12px;display:flex;flex-direction:column;justify-content:center;align-items:center;min-height:110px;text-align:center;">';
        html += '<div style="font-size:0.8em;color:#666;margin-bottom:8px;font-weight:bold;">' + getTranslation('modal.bestScorePartner') + '</div>';
        html += '<div style="font-size:1.1em;font-weight:bold;color:#1e3c72;margin-bottom:6px;word-break:break-word;">' + (bestPartner ? bestPartner[0] : 'N/A') + '</div>';
        html += '<div style="background:#f5576c;color:white;padding:6px 10px;border-radius:4px;text-align:center;font-weight:bold;font-size:0.85em;width:100%;">% ' + (bestPartner ? bestPartner[1].score.toFixed(2) : '-') + '</div>';
        html += '</div>';
        html += '</div>';
        
        content.innerHTML = html;
        console.log('Tab 1 HTML render edildi');
    } else if (tabNum === 2) {
        // Sonuçlar sayfası
        const recordCount = data.length;
        if (title) {
            title.style.fontSize = '1.1em';
            title.textContent = getTranslation('modal.tournamentsAndResults') + ' (' + recordCount + ' ' + getTranslation('modal.gamesLabel') + ')';
        }
        
        // Sıralama uygulaması
        let sorted = [...data];
        if (window.playerSortConfig && window.playerSortConfig.sortBy) {
            sorted.sort((a, b) => {
                let valA, valB;
                if (window.playerSortConfig.sortBy === 'date') {
                    const aDate = a['Tarih'].split('.').reverse().join('');
                    const bDate = b['Tarih'].split('.').reverse().join('');
                    valA = aDate;
                    valB = bDate;
                } else if (window.playerSortConfig.sortBy === 'score') {
                    valA = parseFloat(a['Skor']) || 0;
                    valB = parseFloat(b['Skor']) || 0;
                }
                
                if (window.playerSortConfig.order === 'asc') {
                    return valA < valB ? -1 : valA > valB ? 1 : 0;
                } else {
                    return valA > valB ? -1 : valA < valB ? 1 : 0;
                }
            });
        }
        
        let html = '<div style="display:flex;flex-direction:column;gap:8px;">';
        
        // Liste başlığı
        html += '<div style="display:grid;grid-template-columns:80px 1fr 100px;gap:12px;padding:12px;background:#667eea;color:white;border-radius:8px;font-weight:bold;font-size:0.9em;position:sticky;top:0;z-index:10;">';
        html += '<div style="cursor:pointer;display:flex;align-items:center;justify-content:center;gap:4px;" onclick="togglePlayerSort(\'date\')">' + getTranslation('modal.date') + ' ';
        html += (window.playerSortConfig && window.playerSortConfig.sortBy === 'date' ? (window.playerSortConfig.order === 'asc' ? '▲' : '▼') : '↕');
        html += '</div>';
        html += '<div style="cursor:pointer;display:flex;align-items:center;justify-content:center;gap:4px;" onclick="togglePlayerSort(\'partner\')">' + getTranslation('modal.partner') + '</div>';
        html += '<div style="cursor:pointer;display:flex;align-items:center;justify-content:center;gap:4px;" onclick="togglePlayerSort(\'score\')">' + getTranslation('modal.score') + ' ';
        html += (window.playerSortConfig && window.playerSortConfig.sortBy === 'score' ? (window.playerSortConfig.order === 'asc' ? '▲' : '▼') : '↕');
        html += '</div>';
        html += '</div>';
        
        // Liste satırları
        sorted.forEach((row, idx) => {
            // Tarih formatını dd.mm.yy yaparak göster
            const tarihParts = row['Tarih'].split('.');
            const dateFmt = tarihParts[0] + '.' + tarihParts[1] + '.' + (tarihParts[2].length > 2 ? tarihParts[2].slice(-2) : tarihParts[2]);
            
            // Partner bulurken normalize et
            const oyuncu1Norm = normalizeText(row['Oyuncu 1'].trim().replace(/\s+/g, ' '));
            const oyuncu2Norm = normalizeText(row['Oyuncu 2'].trim().replace(/\s+/g, ' '));
            const partner = oyuncu1Norm === playerName ? row['Oyuncu 2'] : row['Oyuncu 1'];
            const score = parseFloat(row['Skor']);
            
            // Score'a göre renk
            const scoreColor = score >= 50 ? '#16a34a' : '#dc2626';
            const scoreBg = score >= 50 ? '#dcfce7' : '#fee2e2';
            
            html += '<div style="display:grid;grid-template-columns:80px 1fr 100px;gap:12px;padding:12px;background:white;border:1px solid #e5e7eb;border-radius:6px;align-items:center;transition:all 0.2s ease;" ';
            html += 'onmouseover="this.style.background=\'#f3f4f6\';this.style.boxShadow=\'0 4px 12px rgba(0,0,0,0.1)\';" ';
            html += 'onmouseout="this.style.background=\'white\';this.style.boxShadow=\'none\';">';
            
            // Tarih
            html += '<div style="font-weight:600;color:#1e3c72;font-size:0.85em;text-align:center;padding:6px;border-radius:4px;">' + dateFmt + '</div>';
            
            // Partner (geniş alan)
            html += '<div style="color:#374151;font-weight:500;font-size:0.9em;word-break:break-word;padding:6px;background:#f9fafb;border-radius:4px;text-align:center;max-width:100%;overflow:hidden;text-overflow:ellipsis;">' + partner + '</div>';
            
            // Skor
            html += '<div style="font-weight:bold;color:' + scoreColor + ';padding:6px 8px;border-radius:4px;text-align:right;font-size:0.85em;">% ' + score.toFixed(2) + '</div>';
            
            html += '</div>';
        });
        
        html += '</div>';
        content.innerHTML = html;
        console.log('Tab 2 HTML render edildi');
    }
}

function togglePlayerSort(sortBy) {
    if (!window.playerSortConfig) window.playerSortConfig = {};
    
    if (window.playerSortConfig.sortBy === sortBy) {
        window.playerSortConfig.order = window.playerSortConfig.order === 'asc' ? 'desc' : 'asc';
    } else {
        window.playerSortConfig.sortBy = sortBy;
        window.playerSortConfig.order = 'asc';
    }
    
    showPlayerTab(window.currentPlayerTab);
}

// ===== PLAYER NAME SELECTION =====
function selectPlayerName(playerName) {
    const playerInput = document.getElementById('playerName');
    const dropdown = document.getElementById('playerNameSuggestions');
    
    playerInput.value = playerName;
    dropdown.style.display = 'none';
    
    console.log(`Seçilen oyuncu: ${playerName}`);
}

// ===== PLAYER TIME FILTER HANDLER =====
function setPlayerTimeFilter(period, event) {
    console.log('setPlayerTimeFilter çağırıldı:', period, event);
    
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    const playerInput = document.getElementById('playerName');
    const playerName = normalizeText(playerInput.value.trim().replace(/\s+/g, ' '));
    
    console.log('Oyuncu input değeri:', playerName);
    
    if (!playerName) {
        alert('Lütfen oyuncu adı seçin');
        return;
    }
    
    if (!databaseReady) {
        alert('Veritabanı henüz yüklenmedi');
        return;
    }
    
    console.log('Database hazır, filtre başlıyor...');
    
    // Tarih aralığını belirle
    let startDate, endDate;
    let today = new Date();
    
    if (period === 'currentMonth') {
        const currentMonth = today.getMonth();
        const currentYear = today.getFullYear();
        startDate = new Date(currentYear, currentMonth, 1);
        endDate = new Date(currentYear, currentMonth + 1, 0);
    } else if (period === 'currentYear') {
        startDate = new Date(today.getFullYear(), 0, 1);
        endDate = new Date(today.getFullYear(), 11, 31);
    } else if (period === 'last3Years') {
        startDate = new Date(today.getFullYear() - 2, 0, 1);
        endDate = new Date(today.getFullYear(), 11, 31);
    } else if (period === 'since2020') {
        startDate = new Date(2020, 0, 1);
        endDate = new Date(today.getFullYear(), 11, 31);
    }
    
    // Saat ve zaman bilgisini yoksay - endDate'i gün sonuna ayarla
    endDate.setHours(23, 59, 59, 999);
    
    // Oyuncunun sonuçlarını filtrele
    const playerRecords = allData.filter(record => {
        const [day, month, year] = record.Tarih.split('.').map(Number);
        const d = new Date(year, month - 1, day);
        const oyuncu1 = normalizeText(record['Oyuncu 1'].trim().replace(/\s+/g, ' '));
        const oyuncu2 = normalizeText(record['Oyuncu 2'].trim().replace(/\s+/g, ' '));
        return (oyuncu1 === playerName || oyuncu2 === playerName) &&
               d >= startDate && d <= endDate;
    });
    
    if (playerRecords.length === 0) {
        alert(`${playerName} için bu dönemde sonuç bulunamadı`);
        return;
    }
    
    console.log('openPlayerModal çağrılıyor...');
    openPlayerModal(playerName, playerRecords, period);
}

function closeMobileModal() {
    const modal = document.getElementById('mobileResultsModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
    window.dailyModalData = null;
    window.currentDailyTab = 1;
}

// ===== GLOBAL MODAL PAGE NAVIGATION =====
function goToGlobalPage(direction, event) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    let newPage = currentGlobalPage + direction;
    
    // Sayfa sınırlarını kontrol et
    if (newPage < 1) newPage = 1;
    if (newPage > 3) newPage = 3;
    
    if (newPage !== currentGlobalPage) {
        currentGlobalPage = newPage;
        
        // İlgili render fonksiyonunu çağır
        if (currentGlobalPage === 1) {
            renderGlobalPage1();
        } else if (currentGlobalPage === 2) {
            renderGlobalPage2();
        } else if (currentGlobalPage === 3) {
            renderGlobalPage3();
        }
    }
}

function closeGlobalStatsModal() {
    const modal = document.getElementById('globalStatsModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
    currentGlobalPage = 1;
}

// ===== OTOMATİK VERİ GÜNCELLEME SİSTEMİ =====
// Her uygulamaya açılışta ve periyodik olarak yeni veri kontrol et
function setupAutoDataRefresh() {
    console.log('🔄 Otomatik veri güncelleme sistemi başlatılıyor...');
    
    // İlk kontrol: 30 saniye sonra
    setTimeout(() => {
        checkForNewData();
    }, 30000);
    
    // Periyodik kontrol: Her 10 dakikada bir
    setInterval(() => {
        checkForNewData();
    }, 10 * 60 * 1000); // 10 dakika
    
    console.log('✓ Otomatik veri kontrol: Her 10 dakikada bir');
}

function checkForNewData() {
    if (!databaseReady) {
        console.log('⏳ Database henüz hazır değil, kontrol erteleniyor...');
        return;
    }
    
    const lastUpdateKey = 'lastDatabaseUpdate';
    const lastUpdate = localStorage.getItem(lastUpdateKey);
    const currentSize = allData.length;
    
    // Yeni veri kontrolü: database.json'u yükle
    let checkUrl = './database.json?v=' + Date.now();
    
    fetch(checkUrl)
        .then(response => response.json())
        .then(newData => {
            if (!Array.isArray(newData)) {
                console.warn('⚠️ Veri geçersiz format');
                return;
            }
            
            const newSize = newData.length;
            
            // Eğer veri sayısı değiştiyse güncelle
            if (newSize !== currentSize) {
                console.log(`🔄 Yeni veri bulundu! ${currentSize} → ${newSize} kayıt`);
                
                // Database'i güncelle
                allData = newData;
                
                // LocalStorage'a güncelleme zamanını kaydet
                localStorage.setItem(lastUpdateKey, new Date().toISOString());
                
                // Oyuncu listesini yenile
                initializePlayerSearch();
                
                // Bildirim göster
                showDataUpdateNotification(currentSize, newSize);
            } else {
                console.log(`✓ Veri güncel (${currentSize} kayıt)`);
            }
        })
        .catch(err => {
            console.warn('⚠️ Veri kontrol hatası:', err.message);
        });
}

function showDataUpdateNotification(oldSize, newSize) {
    // Sayfanın sol üst köşesine geçici bildirim göster
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        left: 20px;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        font-weight: bold;
        z-index: 99999;
        animation: slideIn 0.3s ease-out;
        max-width: 300px;
        word-wrap: break-word;
    `;
    
    const addedRecords = newSize - oldSize;
    notification.innerHTML = `
        <div>✅ Veritabanı güncellendi!</div>
        <div style="font-size:0.9em;opacity:0.9;margin-top:5px;">${addedRecords > 0 ? '➕ ' + addedRecords + ' yeni kayıt eklendi' : '🔄 ' + Math.abs(addedRecords) + ' kayıt kaldırıldı'}</div>
    `;
    
    document.body.appendChild(notification);
    
    // 4 saniye sonra kaldır
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

// ===== ANİMASYON TI =====
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(-100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(-100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Sayfa yüklendiğinde otomatik sistem başlat
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupAutoDataRefresh);
} else {
    setupAutoDataRefresh();
}

console.log('✓ script.js yüklendi - Tüm fonksiyonlar hazır');
