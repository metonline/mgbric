// Script version for cache busting - v423
const SCRIPT_VERSION = '423';

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

// ===== EL MAPPING HELPER =====
// Database'deki field isimleri rotated - dealer'a göre mapping değişir (clockwise rotation)
function getMappedHands(h, dealerLetter) {
    const dealerIndex = {'N': 0, 'E': 1, 'S': 2, 'W': 3}[dealerLetter] || 0;
    const fields = ['h.S', 'h.N', 'h.W', 'h.E']; // rotation 0 mapping (N dealer)
    
    // Clockwise rotation uygula
    const rotated = [
        fields[(0 - dealerIndex + 4) % 4],  // N
        fields[(1 - dealerIndex + 4) % 4],  // E
        fields[(2 - dealerIndex + 4) % 4],  // S
        fields[(3 - dealerIndex + 4) % 4]   // W
    ];
    
    return {
        'N': h[rotated[0].split('.')[1]],
        'E': h[rotated[1].split('.')[1]],
        'S': h[rotated[2].split('.')[1]],
        'W': h[rotated[3].split('.')[1]]
    };
}

// Dosya bilgisini göster (dil değişiklikleri için dinamik)
function formatNumber(num) {
    /**Format number with thousands separator based on current language*/
    // Turkish style: 55.996 (uses periods)
    // English style: 55,996 (uses commas)
    // Get language from localStorage to ensure it matches the current UI language
    const lang = localStorage.getItem('language') || localStorage.getItem('appLanguage') || 'tr';
    const separator = lang === 'tr' ? '.' : ',';
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, separator);
}

function updateFileInfo() {
    if (!allData || allData.length === 0) {
        return;
    }
    const lastDate = getLastDateFromDatabase();
    const formattedCount = formatNumber(allData.length);
    const msg = getTranslation('results.databaseUpdated')
        .replace('{date}', lastDate)
        .replace('{count}', formattedCount);
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
        filtered.forEach((row, idx) => {
            const eventId = extractEventIdFromLink(row['Link']);
            const pairNum = row['Sıra'];
            const p1 = row['Oyuncu 1'];
            const p2 = row['Oyuncu 2'];
            
            html += `<div class="clickable-pair" data-event="${eventId || ''}" data-pair="${pairNum}" data-direction="NS" data-names="${p1} &amp; ${p2}"
                         style="background:${bg};border-radius:8px;padding:12px 16px;margin-bottom:12px;cursor:pointer;transition:all 0.2s;" 
                         onmouseover="this.style.background='#d0edf5'" onmouseout="this.style.background='${bg}'">`;
            html += `<div style="display:flex;justify-content:space-between;align-items:center;">`;
            html += `<div style="font-weight:bold;">[${row['Sıra']}] ${p1} - ${p2}</div>`;
            html += `<div style="color:${color};font-weight:bold;">% ${row['Skor']}</div>`;
            html += `</div>`;
            if (eventId) html += `<div style="font-size:0.75em;color:#6366f1;margin-top:4px;">📋 Tıklayın → Oynadıkları Eller</div>`;
            html += `</div>`;
        });
        if (filtered.length === 0) {
            html += `<div style='text-align:center;color:#999;font-size:1.1em;margin-top:24px;'>Sonuç bulunamadı.</div>`;
        }
        content.innerHTML = html;
        
        // Event delegation for clickable pairs
        content.querySelectorAll('.clickable-pair').forEach(el => {
            el.addEventListener('click', function() {
                const eventId = this.dataset.event;
                const pairNum = this.dataset.pair;
                const direction = this.dataset.direction;
                const names = this.dataset.names;
                if (eventId) {
                    openPairSummaryModal(eventId, pairNum, direction, names);
                }
            });
        });
        
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
        let html = `<h2 style="text-align:center;color:${color};margin:16px 0 20px 0;font-size:1.2em;">${title}</h2>`;
        filtered.forEach((row, idx) => {
            const eventId = extractEventIdFromLink(row['Link']);
            const pairNum = row['Sıra'];
            const p1 = row['Oyuncu 1'];
            const p2 = row['Oyuncu 2'];
            
            html += `<div class="clickable-pair" data-event="${eventId || ''}" data-pair="${pairNum}" data-direction="EW" data-names="${p1} &amp; ${p2}"
                         style="background:${bg};border-radius:8px;padding:12px 16px;margin-bottom:12px;cursor:pointer;transition:all 0.2s;" 
                         onmouseover="this.style.background='#e0f5d8'" onmouseout="this.style.background='${bg}'">`;
            html += `<div style="display:flex;justify-content:space-between;align-items:center;">`;
            html += `<div style="font-weight:bold;">[${row['Sıra']}] ${p1} - ${p2}</div>`;
            html += `<div style="color:${color};font-weight:bold;">% ${row['Skor']}</div>`;
            html += `</div>`;
            if (eventId) html += `<div style="font-size:0.75em;color:#6366f1;margin-top:4px;">📋 Tıklayın → Oynadıkları Eller</div>`;
            html += `</div>`;
        });
        if (filtered.length === 0) {
            html += `<div style='text-align:center;color:#999;font-size:1.1em;margin-top:24px;'>Sonuç bulunamadı.</div>`;
        }
        content.innerHTML = html;
        
        // Event delegation for clickable pairs
        content.querySelectorAll('.clickable-pair').forEach(el => {
            el.addEventListener('click', function() {
                const eventId = this.dataset.event;
                const pairNum = this.dataset.pair;
                const direction = this.dataset.direction;
                const names = this.dataset.names;
                if (eventId) {
                    openPairSummaryModal(eventId, pairNum, direction, names);
                }
            });
        });
        
        const footer = document.getElementById('globalNavFooter');
        if (footer) {
            footer.style.display = 'flex';
            footer.innerHTML = `<button onclick="goToGlobalPage(-1, event)" style="flex:1;padding:10px;background:#17a2b8;color:white;border:none;cursor:pointer;margin:5px;">← Önceki</button><div style="flex:1;text-align:center;padding:10px;background:#f0f0f0;margin:5px;border-radius:4px;">Sayfa 3/3</div><button onclick="closeGlobalStatsModal()" style="flex:1;padding:10px;background:#6c757d;color:white;border:none;cursor:pointer;margin:5px;">Kapat ✕</button>`;
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
        <div style="color:#1ca7c1;font-weight:bold;font-size:1.1em;margin-bottom:8px;">Kuzey-Güney</div>`;
    nsChamps.forEach(champ => {
        const eventId = extractEventIdFromLink(champ['Link']);
        const pairNum = champ['Sıra'];
        const p1 = champ['Oyuncu 1'];
        const p2 = champ['Oyuncu 2'];
        
        nsHTML += `<div class="clickable-pair" data-event="${eventId || ''}" data-pair="${pairNum}" data-direction="NS" data-names="${p1} &amp; ${p2}" 
                       style="background:white;padding:8px 12px;border-radius:6px;margin-bottom:6px;cursor:pointer;transition:all 0.2s;"
                       onmouseover="this.style.background='#d0edf5'" onmouseout="this.style.background='white'">
            <div style="font-weight:bold;">${p1} - ${p2}</div>
            <div style="display:flex;justify-content:space-between;align-items:center;margin-top:4px;">
                <span style="color:#1ca7c1;font-weight:bold;">% ${champ['Skor']}</span>
                ${eventId ? '<span style="font-size:0.75em;color:#6366f1;">📋 Tıkla → Eller</span>' : ''}
            </div>
        </div>`;
    });
    nsHTML += `</div>`;
    // EW kutu
    let ewHTML = `<div style="background:#f0faea;border-radius:8px;padding:12px 16px;margin-bottom:12px;">
        <div style="color:#6db66d;font-weight:bold;font-size:1.1em;margin-bottom:8px;">Doğu-Batı</div>`;
    ewChamps.forEach(champ => {
        const eventId = extractEventIdFromLink(champ['Link']);
        const pairNum = champ['Sıra'];
        const p1 = champ['Oyuncu 1'];
        const p2 = champ['Oyuncu 2'];
        
        ewHTML += `<div class="clickable-pair" data-event="${eventId || ''}" data-pair="${pairNum}" data-direction="EW" data-names="${p1} &amp; ${p2}"
                       style="background:white;padding:8px 12px;border-radius:6px;margin-bottom:6px;cursor:pointer;transition:all 0.2s;"
                       onmouseover="this.style.background='#e0f5d8'" onmouseout="this.style.background='white'">
            <div style="font-weight:bold;">${p1} - ${p2}</div>
            <div style="display:flex;justify-content:space-between;align-items:center;margin-top:4px;">
                <span style="color:#6db66d;font-weight:bold;">% ${champ['Skor']}</span>
                ${eventId ? '<span style="font-size:0.75em;color:#6366f1;">📋 Tıkla → Eller</span>' : ''}
            </div>
        </div>`;
    });
    ewHTML += `</div>`;
    statsGrid.innerHTML = `<div>${nsHTML}${ewHTML}</div>`;
    
    // Event delegation for clickable pairs
    statsGrid.querySelectorAll('.clickable-pair').forEach(el => {
        el.addEventListener('click', function() {
            const eventId = this.dataset.event;
            const pairNum = this.dataset.pair;
            const direction = this.dataset.direction;
            const names = this.dataset.names;
            if (eventId) {
                openPairSummaryModal(eventId, pairNum, direction, names);
            }
        });
    });
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
    let hoverBg = direction === 'NS' ? '#d0edf5' : '#e0f5d8';
    let title = direction === 'NS' ? 'Kuzey-Güney Sonuçları' : 'Doğu-Batı Sonuçları';
    let html = `<div id="directionResultsContainer" style="background:${bg};border-radius:8px;padding:12px 8px 8px 8px;margin-bottom:12px;">
        <div style="color:${color};font-weight:bold;font-size:1.1em;text-align:center;margin-bottom:10px;">${title}</div>`;
    filtered.forEach(row => {
        const eventId = extractEventIdFromLink(row['Link']);
        const pairNum = row['Sıra'];
        const p1 = row['Oyuncu 1'];
        const p2 = row['Oyuncu 2'];
        
        html += `<div class="clickable-pair" data-event="${eventId || ''}" data-pair="${pairNum}" data-direction="${direction}" data-names="${p1} &amp; ${p2}"
                     style="background:white;border-radius:6px;padding:8px 10px;margin-bottom:8px;border-left:4px solid ${color};cursor:pointer;transition:all 0.2s;"
                     onmouseover="this.style.background='${hoverBg}'" onmouseout="this.style.background='white'">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="font-weight:bold;">[${row['Sıra']}] ${p1} - ${p2}</span>
                <span style="color:${color};font-weight:bold;">% ${row['Skor']}</span>
            </div>
            ${eventId ? '<div style="font-size:0.75em;color:#6366f1;margin-top:4px;">📋 Tıklayın → Oynadıkları Eller</div>' : ''}
        </div>`;
    });
    html += `</div>`;
    if (filtered.length === 0) {
        html += `<div style='text-align:center;color:#999;font-size:1.1em;margin-top:24px;'>Sonuç bulunamadı.</div>`;
    }
    if (resultsGrid) {
        resultsSection.style.display = 'block';
        resultsGrid.innerHTML = html;
        
        // Event delegation for clickable pairs
        resultsGrid.querySelectorAll('.clickable-pair').forEach(el => {
            el.addEventListener('click', function() {
                const eventId = this.dataset.event;
                const pairNum = this.dataset.pair;
                const dir = this.dataset.direction;
                const names = this.dataset.names;
                if (eventId) {
                    openPairSummaryModal(eventId, pairNum, dir, names);
                }
            });
        });
    } else {
        // Fallback: render directly into modal content
        const modalContent = document.getElementById('globalModalContent');
        if (modalContent) {
            modalContent.innerHTML = html;
            
            // Event delegation for clickable pairs
            modalContent.querySelectorAll('.clickable-pair').forEach(el => {
                el.addEventListener('click', function() {
                    const eventId = this.dataset.event;
                    const pairNum = this.dataset.pair;
                    const dir = this.dataset.direction;
                    const names = this.dataset.names;
                    if (eventId) {
                        openPairSummaryModal(eventId, pairNum, dir, names);
                    }
                });
            });
        }
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
        return new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
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

    // TARIH ARILIGI: 2 sayfa modal aç (İstatistikler, Sonuçlar)
    console.log('🔔 openRangeModal2Pages çağrılmak üzere:', globalModalData.length, 'kayıt');
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
    // selectedDate format: DD.MM.YYYY (e.g., "16.01.2026")
    const filterDate = selectedDateInput.value.trim();
    
    // Validate format
    const dateRegex = /^\d{2}\.\d{2}\.\d{4}$/;
    if (!dateRegex.test(filterDate)) {
        alert('Lütfen tarih formatını GG.AA.YYYY olarak girin (örn: 16.01.2026)');
        return;
    }
    
    console.log(`🔍 Seçilen tarih: ${filterDate}`);
    console.log(`📊 Toplam kayıt: ${allData.length}`);
    
    // Debug: Show sample dates from database
    if (allData.length > 0) {
        const sampleDates = [...new Set(allData.slice(0, 100).map(r => r.Tarih))];
        console.log(`📅 Veritabanında örnek tarihler: ${sampleDates.join(', ')}`);
    }
    
    const filtered = allData.filter(record => record.Tarih === filterDate);
    console.log(`✅ Filtrelenen kayıt: ${filtered.length}`);
    console.log(`📋 Filtrelenen ilk 3 kayıt:`, filtered.slice(0, 3));
    
    if (filtered.length === 0) {
        alert(`${filterDate} tarihinde kayıt bulunamadı`);
        return;
    }
    // Farklı turnuva isimlerini bul
    const uniqueTournaments = [...new Set(filtered.map(r => r.Turnuva || ''))];
    console.log(`🎯 Bulunan turnuvalar: ${uniqueTournaments.join(', ')}`);
    
    if (uniqueTournaments.length > 1) {
        // Kullanıcıya seçim sun
        showTournamentSelectModal(uniqueTournaments, function(selectedTournament) {
            const tournamentData = filtered.filter(r => (r.Turnuva || '') === selectedTournament);
            showMobileModal(tournamentData, filterDate);
        });
    } else {
        showMobileModal(filtered, filterDate);
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
    // Eğer modalType set edilmemişse, default olarak 'range-filter'
    if (!window.modalType) {
        window.modalType = 'range-filter';
    }
    
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
        visibility: visible;
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
        visibility: visible;
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
    pageIndicator.textContent = 'Sayfa 1/4';
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
    
    // Initialize swipe navigation for 4 pages
    initGlobalRangeSwipe();
    
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

// Toggle hands details visibility
function toggleHandsDetails(date) {
    const handsDiv = document.getElementById(`hands-${date}`);
    if (handsDiv) {
        handsDiv.style.display = handsDiv.style.display === 'none' ? 'block' : 'none';
    }
}

// ===== GLOBAL RANGE SWIPE NAVIGATION (4 PAGES) =====
function initGlobalRangeSwipe() {
    const modal = document.getElementById('globalRangeModal');
    if (!modal) {
        console.warn('⚠️ globalRangeModal bulunamadı');
        return;
    }
    
    let touchStartX = 0;
    let touchStartY = 0;
    let touchEndX = 0;
    let touchEndY = 0;
    let isSwiping = false;
    
    console.log('✓ Global Range Swipe navigation initialized');
    
    modal.addEventListener('touchstart', (e) => {
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
        isSwiping = true;
    });
    
    modal.addEventListener('touchmove', (e) => {
        if (!isSwiping) return;
        // Prevent default scroll behavior during swipe
        if (Math.abs(e.touches[0].clientX - touchStartX) > 10) {
            e.preventDefault();
        }
    });
    
    modal.addEventListener('touchend', (e) => {
        if (!isSwiping) return;
        isSwiping = false;
        
        touchEndX = e.changedTouches[0].clientX;
        touchEndY = e.changedTouches[0].clientY;
        handleGlobalRangeSwipe();
    });
    
    function handleGlobalRangeSwipe() {
        const swipeThreshold = 40;
        const verticalThreshold = 40;
        
        const diffX = touchStartX - touchEndX;
        const diffY = Math.abs(touchStartY - touchEndY);
        
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
            console.log('🔄 Sola swipe - Sonraki sayfa');
            showGlobalRangeTab(window.currentRangeTab + 1);
        }
        // Sağa swipe (diffX negative) → Önceki sayfa
        else if (diffX < -swipeThreshold) {
            console.log('🔄 Sağa swipe - Önceki sayfa');
            showGlobalRangeTab(window.currentRangeTab - 1);
        }
    }
}

function showGlobalRangeTab(tabNum) {
    try {
        // Boundary check - 4 sayfaya çıkardık
        if (tabNum < 1) tabNum = 1;
        if (tabNum > 4) tabNum = 4;
        
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
    
    // Update page indicator - 4 sayfa göster
    if (pageIndicator) pageIndicator.textContent = `Sayfa ${tabNum}/4`;
    
    // Update button visibility
    if (prevBtn) prevBtn.style.visibility = tabNum > 1 ? 'visible' : 'hidden';
    if (nextBtn) nextBtn.style.visibility = tabNum < 4 ? 'visible' : 'hidden';
    
    if (tabNum === 1) {
        // Sayfa 1: Modalun türüne göre farklı içerik
        console.log('📄 Tab 1 başladı, modalType:', window.modalType);
        
        if (window.modalType === 'date-picker') {
            // TARİH SEÇİCİ: Günün Şampiyonları (1.likler)
            if (title) title.textContent = '🏆 Günün Şampiyonları';
            
            const champions = data.filter(row => parseInt(row['Sıra']) === 1);
            
            let html = '<div style="display:flex;flex-direction:column;gap:10px;max-height:100%;overflow-y:auto;">';
            
            if (champions.length === 0) {
                html += '<p style="text-align:center;color:#999;padding:20px;">Şampiyon bulunamadı</p>';
            } else {
                champions.forEach((record, idx) => {
                    const eventId = extractEventIdFromLink(record['Link']);
                    const pairNum = record['Sıra'];
                    const p1 = record['Oyuncu 1'];
                    const p2 = record['Oyuncu 2'];
                    const direction = record['Direction'] || 'NS';
                    const dirColor = direction === 'NS' ? '#3b82f6' : '#10b981';
                    
                    html += `
                        <div class="clickable-pair" data-event="${eventId || ''}" data-pair="${pairNum}" data-direction="${direction}" data-names="${p1} &amp; ${p2}"
                             style="padding:12px;background:#f8f9fa;border-left:4px solid #ffc107;border-radius:6px;cursor:pointer;transition:all 0.2s;" 
                             onmouseover="this.style.background='#fff3cd'" onmouseout="this.style.background='#f8f9fa'">
                            <div style="display:flex;justify-content:space-between;align-items:center;">
                                <div style="font-weight:bold;color:#1e3c72;">
                                    🥇 ${idx + 1}. ${p1} & ${p2}
                                </div>
                                <span style="background:${dirColor};color:white;padding:2px 6px;border-radius:4px;font-size:0.75em;font-weight:bold;">${direction}</span>
                            </div>
                            <div style="font-size:0.85em;color:#666;margin-top:5px;">
                                📊 %${record['Skor']} | 🎯 ${record['Turnuva Adı'] || 'Bilinmeyen'}
                            </div>
                            ${eventId ? '<div style="font-size:0.75em;color:#6366f1;margin-top:4px;">📋 Tıklayın → Oynadıkları Eller</div>' : ''}
                        </div>
                    `;
                });
            }
            
            html += '</div>';
            contentArea.innerHTML = html;
            
            // Event delegation for clickable pairs
            contentArea.querySelectorAll('.clickable-pair').forEach(el => {
                el.addEventListener('click', function() {
                    const eventId = this.dataset.event;
                    const pairNum = this.dataset.pair;
                    const direction = this.dataset.direction;
                    const names = this.dataset.names;
                    if (eventId) {
                        openPairSummaryModal(eventId, pairNum, direction, names);
                    }
                });
            });
            
        } else {
            // RANGE FİLTRELER: İstatistikler (Top 1.likler + Top Skor Ortalaması)
            if (title) title.textContent = '📊 İstatistikler';
            
            // Top 3 1.lik Kazananlar
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
            
            // Top 3 Skor Ortalaması
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
            
            contentArea.innerHTML = html;
        }
        
    } else if (tabNum === 2) {
        // Sayfa 2: Modalun türüne göre farklı içerik
        if (window.modalType === 'date-picker') {
            // TARİH SEÇİCİ: NS Skor Sıralaması
            if (title) title.textContent = '🎲 NS Skor Sıralaması';
            
            const nsList = data.filter(row => row['Direction'] === 'NS').sort((a, b) => parseFloat(b['Skor']) - parseFloat(a['Skor']));
            
            let html = '<div style="display:flex;flex-direction:column;gap:8px;max-height:100%;overflow-y:auto;">';
            
            if (nsList.length === 0) {
                html += '<p style="text-align:center;color:#999;padding:20px;">NS sonuç bulunamadı</p>';
            } else {
                nsList.forEach((record, idx) => {
                    // Extract event ID from Link
                    const eventId = extractEventIdFromLink(record['Link']);
                    const pairNum = record['Sıra'];
                    const p1 = record['Oyuncu 1'];
                    const p2 = record['Oyuncu 2'];
                    
                    html += `
                        <div class="clickable-pair" data-event="${eventId || ''}" data-pair="${pairNum}" data-direction="NS" data-names="${p1} &amp; ${p2}"
                             style="padding:10px;background:#f8f9fa;border-left:4px solid #3b82f6;border-radius:6px;display:flex;justify-content:space-between;align-items:center;cursor:pointer;transition:all 0.2s;"
                             onmouseover="this.style.background='#e0e7ff'" onmouseout="this.style.background='#f8f9fa'">
                            <div style="flex:1;">
                                <div style="font-weight:bold;color:#1e3c72;font-size:0.9em;">${idx + 1}. ${p1} & ${p2}</div>
                                ${eventId ? '<div style="font-size:0.7em;color:#6366f1;margin-top:2px;">📋 Tıklayın → Eller</div>' : ''}
                            </div>
                            <div style="display:flex;align-items:center;gap:10px;">
                                <div style="font-weight:bold;color:#3b82f6;font-size:1em;">%${record['Skor']}</div>
                            </div>
                        </div>
                    `;
                });
            }
            
            html += '</div>';
            contentArea.innerHTML = html;
            
            // Event delegation for clickable pairs
            contentArea.querySelectorAll('.clickable-pair').forEach(el => {
                el.addEventListener('click', function() {
                    const eventId = this.dataset.event;
                    const pairNum = this.dataset.pair;
                    const direction = this.dataset.direction;
                    const names = this.dataset.names;
                    if (eventId) {
                        openPairSummaryModal(eventId, pairNum, direction, names);
                    }
                });
            });
            
        } else {
            // GLOBAL FİLTRELER: Turnuva Sonuçları (Tarih | NS-1 | Oyuncu 1 | Oyuncu 2 | % Skor)
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
    } else if (tabNum === 3) {
        if (window.modalType === 'date-picker') {
            // DATE PICKER: EW Sıralama
            if (title) title.textContent = '🎯 EW Sıralama';
            const ewList = data.filter(row => row['Direction'] === 'EW')
                .sort((a, b) => parseFloat(b['Skor']) - parseFloat(a['Skor']));
            
            let html = '<div style="display:flex;flex-direction:column;gap:8px;padding:8px;">';
            
            if (ewList.length === 0) {
                html += '<div style="text-align:center;color:#999;padding:40px;">Bu tarihe ait EW verisi bulunamadı</div>';
            } else {
                ewList.forEach((row, idx) => {
                    const score = parseFloat(row['Skor']) || 0;
                    const scoreColor = score >= 50 ? '#16a34a' : '#dc2626';
                    
                    // Extract event ID from Link
                    const eventId = extractEventIdFromLink(row['Link']);
                    const pairNum = row['Sıra'];
                    const p1 = row['Oyuncu 1'];
                    const p2 = row['Oyuncu 2'];
                    const bgColor = idx % 2 === 0 ? '#f0fdf4' : 'white';
                    
                    html += `
                        <div class="clickable-pair" data-event="${eventId || ''}" data-pair="${pairNum}" data-direction="EW" data-names="${p1} &amp; ${p2}" data-bg="${bgColor}"
                             style="padding:10px;background:${bgColor};border-left:4px solid #10b981;border-radius:6px;display:flex;justify-content:space-between;align-items:center;cursor:pointer;transition:all 0.2s;"
                             onmouseover="this.style.background='#dcfce7'" onmouseout="this.style.background='${bgColor}'">
                            <div style="flex:1;">
                                <div style="font-weight:bold;color:#1e3c72;font-size:0.9em;">${idx + 1}. ${p1} & ${p2}</div>
                                ${eventId ? '<div style="font-size:0.7em;color:#6366f1;margin-top:2px;">📋 Tıklayın → Eller</div>' : ''}
                            </div>
                            <div style="font-weight:bold;color:${scoreColor};font-size:1em;">%${score.toFixed(2)}</div>
                        </div>
                    `;
                });
            }
            
            html += '</div>';
            contentArea.innerHTML = html;
            
            // Event delegation for clickable pairs
            contentArea.querySelectorAll('.clickable-pair').forEach(el => {
                el.addEventListener('click', function() {
                    const eventId = this.dataset.event;
                    const pairNum = this.dataset.pair;
                    const direction = this.dataset.direction;
                    const names = this.dataset.names;
                    if (eventId) {
                        openPairSummaryModal(eventId, pairNum, direction, names);
                    }
                });
            });
        } else {
            // GLOBAL FİLTRELER: Ek İstatistikler (Placeholder)
            if (title) title.textContent = '📈 Ek İstatistikler';
            contentArea.innerHTML = '<div style="text-align:center;color:#999;padding:40px;"><p>Bu sayfa gelecek güncellemeler için ayrılmıştır.</p></div>';
        }
    } else if (tabNum === 4) {
        // Sayfa 4: Placeholder
        if (title) title.textContent = '📋 Sayfası';
        let html = '<div style="text-align:center;color:#999;padding:40px;"><p>Bu sayfa gelecek güncellemeler için ayrılmıştır.</p></div>';
        contentArea.innerHTML = html;
    }
    } catch (error) {
        console.error('❌ showGlobalRangeTab error:', error);
    }
}

// ===== MODAL OPENING =====
function openGlobalStatsModal(data, filterLabel) {
    // BELİRLİ TARIH: 4 sayfa modal aç (İstatistikler, Sonuçlar, Ek İstatistikler, Kişi Performansı)
    window.globalRangeData = data;
    window.modalType = 'date-picker';  // Bu flag'i kullan, showGlobalRangeTab'da içeriği değiştir
    openGlobalRangeModal(data, filterLabel);
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
        // Load data from JSON file directly
        let mainUrl = './database.json?v=' + Date.now();
        let fallbackUrl = './database_temp.json?v=' + Date.now();
        
        // Try main file first
        fetch(mainUrl)
            .then(response => {
                if (!response.ok) throw new Error('Database file not found');
                return response.json();
            })
            .then(data => {
                // Convert dict format to array if needed
                let arrayData = data;
                if (!Array.isArray(data)) {
                    if (data.legacy_records) {
                        // Use legacy_records only (don't mix with events)
                        arrayData = data.legacy_records;
                    } else if (data.records) {
                        arrayData = data.records;
                    }
                }
                
                if (!Array.isArray(arrayData) || arrayData.length === 0) {
                    throw new Error('Database is empty');
                }
                
                console.log(`✅ File loaded ${arrayData.length} records`);
                allData = arrayData;
                updateFileInfo();
                databaseReady = true;
                setDefaultDateToLatest();  // Set latest date as default in input
                initializePlayerSearch();
                if (queuedModalOpen) {
                    openGlobalStatsModal(...queuedModalOpen);
                    queuedModalOpen = null;
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

function showMobileModal(data, filterDate) {
    console.log('showMobileModal çağrıldı, veri:', data ? data.length : 'NULL');
    if (!data || data.length === 0) {
        console.warn('⚠️ showMobileModal: Veri boş!');
        // Yine devam et, boş modal göster
        data = [];
    }
    
    window.currentDailyTab = 1;
    window.dailyModalData = data;
    window.dailyModalDate = filterDate;
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
    if (tabNum > 4) tabNum = 4;
    
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
    if (nextBtn) nextBtn.style.visibility = tabNum < 4 ? 'visible' : 'hidden';
    
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
                const eventId = extractEventIdFromLink(champ['Link']);
                const pairNum = champ['Pair'] || '1';
                const p1 = (champ['Oyuncu 1'] || '').replace(/'/g, "\\'");
                const p2 = (champ['Oyuncu 2'] || '').replace(/'/g, "\\'");
                html += `<div class="clickable-pair" data-event="${eventId || ''}" data-pair="${pairNum}" data-direction="NS" data-names="${p1} &amp; ${p2}" style='padding:8px;background:white;border-radius:4px;text-align:center;cursor:pointer;'>`;
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
                const eventId = extractEventIdFromLink(champ['Link']);
                const pairNum = champ['Pair'] || '1';
                const p1 = (champ['Oyuncu 1'] || '').replace(/'/g, "\\'");
                const p2 = (champ['Oyuncu 2'] || '').replace(/'/g, "\\'");
                html += `<div class="clickable-pair" data-event="${eventId || ''}" data-pair="${pairNum}" data-direction="EW" data-names="${p1} &amp; ${p2}" style='padding:8px;background:white;border-radius:4px;text-align:center;cursor:pointer;'>`;
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
                const eventId = extractEventIdFromLink(row['Link']);
                const pairNum = row['Pair'] || '1';
                const p1 = (row['Oyuncu 1'] || '').replace(/'/g, "\\'");
                const p2 = (row['Oyuncu 2'] || '').replace(/'/g, "\\'");
                html += `<div class="clickable-pair" data-event="${eventId || ''}" data-pair="${pairNum}" data-direction="NS" data-names="${p1} &amp; ${p2}" style='background:#eaf6fb;border-radius:8px;padding:10px;display:flex;align-items:center;gap:8px;cursor:pointer;'>`;
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
                const eventId = extractEventIdFromLink(row['Link']);
                const pairNum = row['Pair'] || '1';
                const p1 = (row['Oyuncu 1'] || '').replace(/'/g, "\\'");
                const p2 = (row['Oyuncu 2'] || '').replace(/'/g, "\\'");
                html += `<div class="clickable-pair" data-event="${eventId || ''}" data-pair="${pairNum}" data-direction="EW" data-names="${p1} &amp; ${p2}" style='background:#f0faea;border-radius:8px;padding:10px;display:flex;align-items:center;gap:8px;cursor:pointer;'>`;
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
    } else if (tabNum === 4) {
        // Tab 4: Turnuva Elleri
        const displayDate = window.dailyModalDate || window.selectedDate || '17.01.2026';
        if (header) header.textContent = `🎴 Turnuva Elleri (${displayDate})`;
        
        // openHandsModal fonksiyonunu çağır
        const selectedDate = displayDate;
        fetch('/hands_database.json')
            .then(r => r.json())
            .then(handsData => {
                const hands = handsData.filter(h => h.date === selectedDate);
                
                if (hands.length === 0) {
                    if (contentArea) contentArea.innerHTML = `<div style='text-align:center;color:#999;'>Bu tarih için el bulunamadı</div>`;
                    return;
                }
                
                // Sort all hands by board number and remove duplicates (keep first occurrence)
                const seenBoards = new Set();
                const uniqueHands = hands.filter(h => {
                    if (seenBoards.has(h.board)) {
                        return false;
                    }
                    seenBoards.add(h.board);
                    return true;
                });
                const sortedHands = uniqueHands.sort((a, b) => a.board - b.board);
                
                // Store all hands globally for modal access
                window.allHandsTab4 = sortedHands;
                
                let html = `<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 15px;">`;
                
                sortedHands.forEach((h, index) => {
                        const dealerLetters = ['N', 'E', 'S', 'W'];
                        const dealerLetter = dealerLetters[(h.board - 1) % 4];
                        const dealerMap = {'N':'1','E':'2','S':'3','W':'4'};
                        const vulnMap = {'None':'0','NS':'1','EW':'2','Both':'3'};
                        const d = dealerMap[dealerLetter] || '1';
                        const v = vulnMap[h.vulnerability] || '0';
                        
                        // Get hands with rotation based on dealer
                        const mappedFields = getMappedHands(h, dealerLetter);
                        
                        // Convert hand string to LIN format (Spades.Hearts.Diamonds.Clubs)
                        const hands = {
                            'N': `S${mappedFields.N?.split('.')[0] || ''}H${mappedFields.N?.split('.')[1] || ''}D${mappedFields.N?.split('.')[2] || ''}C${mappedFields.N?.split('.')[3] || ''}`,
                            'E': `S${mappedFields.E?.split('.')[0] || ''}H${mappedFields.E?.split('.')[1] || ''}D${mappedFields.E?.split('.')[2] || ''}C${mappedFields.E?.split('.')[3] || ''}`,
                            'S': `S${mappedFields.S?.split('.')[0] || ''}H${mappedFields.S?.split('.')[1] || ''}D${mappedFields.S?.split('.')[2] || ''}C${mappedFields.S?.split('.')[3] || ''}`,
                            'W': `S${mappedFields.W?.split('.')[0] || ''}H${mappedFields.W?.split('.')[1] || ''}D${mappedFields.W?.split('.')[2] || ''}C${mappedFields.W?.split('.')[3] || ''}`
                        };
                        console.log(`Board ${h.board} (Dealer: ${dealerLetter}) - N: ${hands.N} | E: ${hands.E} | S: ${hands.S} | W: ${hands.W}`);
                        
                        // Order hands starting from dealer, but only output 3 hands (BBO calculates 4th)
                        const dealerOrder = {'N': ['N', 'E', 'S'], 'E': ['E', 'S', 'W'], 'S': ['S', 'W', 'N'], 'W': ['W', 'N', 'E']};
                        const orderedHands = dealerOrder[dealerLetter] || ['N', 'E', 'S'];
                        const handString = orderedHands.map(pos => hands[pos]).join(',');
                        
                        const lin = `qx|o1|md|${d}${handString},|rh||ah|Board ${h.board}|sv|${v}|pg||`;
                        const iframeUrl = `https://www.bridgebase.com/tools/handviewer.html?bbo=y&lin=${encodeURIComponent(lin)}`;
                        
                        // DD tables disabled
                        let ddTableHtml = '';
                        
                        html += `<div style="background: white; padding: 12px; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); cursor: pointer;" onclick="openHandCardModalByIndex(${index})" title="Detaylı görmek için tıklayın">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; font-size: 0.9rem; color: #666;">
                                <span><strong>Dealer:</strong> ${dealerLetter}</span>
                                <span style="font-weight: bold; color: #1e3c72;">Board ${h.board}</span>
                                <span><strong>Vuln:</strong> ${h.vulnerability}</span>
                            </div>
                            
                            <iframe src="${iframeUrl}" style="width: 100%; height: 320px; border: 1px solid #ddd; border-radius: 4px;" onclick="event.stopPropagation();"></iframe>
                        </div>`;
                });
                
                html += `</div>`;
                if (contentArea) contentArea.innerHTML = html;
            })
            .catch(e => {
                if (contentArea) contentArea.innerHTML = `<div style='color: red;'>Hata: ${e.message}</div>`;
            });
    }
}

// ===== EL KARTI MODAL FONKSIYONLARI =====
function openHandCardModalByIndex(index) {
    if (!window.allHandsTab4 || !window.allHandsTab4[index]) {
        console.error('Hand data not found at index:', index);
        return;
    }
    
    const handData = window.allHandsTab4[index];
    openHandCardModal(handData);
}

function openHandCardModal(handData) {
    const modal = document.getElementById('handsModal');
    const header = modal.querySelector('h2');
    const content = document.getElementById('handsModalContent');
    
    if (!modal || !content) {
        console.error('❌ Modal elements not found');
        return;
    }
    
    console.log('✅ Opening hand card modal for board:', handData.board);
    console.log('DD Analysis data:', JSON.stringify(handData.dd_analysis));
    
    // Modal başlığını güncelle
    if (header) {
        header.textContent = `🎴 Board ${handData.board} - Detaylı Görüntüleme`;
    }
    
    // createHandCard fonksiyonunu çağır ve sonucunu modal'da göster
    const cardHtml = createHandCard(handData);
    console.log('Card HTML generated, length:', cardHtml.length);
    content.innerHTML = cardHtml;
    
    modal.style.display = 'block';
    console.log('✅ Modal displayed');
    
    // Force DD table colors - Use setProperty with !important
    const fixColors = () => {
        const allCells = content.querySelectorAll('td[data-suit]');
        console.log('Found cells with data-suit:', allCells.length);
        
        allCells.forEach(cell => {
            const suit = cell.getAttribute('data-suit');
            
            if (suit === 'heart' || suit === 'diamond') {
                // Red for hearts and diamonds - FORCE with setProperty
                cell.style.setProperty('color', '#e41e3f', 'important');
                cell.style.setProperty('background-color', '#ffccdd', 'important');
                // Also remove any conflicting inline style attribute
                cell.setAttribute('style', cell.getAttribute('style') + '; color: #e41e3f !important; background-color: #ffccdd !important;');
                console.log('✅ Set', suit, 'to RED');
            } else if (suit === 'spade' || suit === 'club') {
                // Black for spades and clubs - FORCE with setProperty
                cell.style.setProperty('color', '#000', 'important');
                cell.style.setProperty('background-color', '#f0f0f0', 'important');
                cell.setAttribute('style', cell.getAttribute('style') + '; color: #000 !important; background-color: #f0f0f0 !important;');
                console.log('✅ Set', suit, 'to BLACK');
            }
        });
    };
    
    // Run multiple times to ensure it sticks
    fixColors();
    setTimeout(fixColors, 5);
    setTimeout(fixColors, 15);
    setTimeout(fixColors, 50);
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
            let convertedData = newData;
            
            // Convert dict format to array if needed
            if (!Array.isArray(newData)) {
                if (newData.legacy_records) {
                    // Use legacy_records only (don't mix with events)
                    convertedData = newData.legacy_records;
                } else if (newData.records) {
                    convertedData = newData.records;
                } else {
                    convertedData = [];
                }
            }
            
            if (!Array.isArray(convertedData) || convertedData.length === 0) {
                console.warn('⚠️ Veri geçersiz format');
                return;
            }
            
            const newSize = convertedData.length;
            
            // Eğer veri sayısı değiştiyse güncelle
            if (newSize !== currentSize) {
                console.log(`🔄 Yeni veri bulundu! ${currentSize} → ${newSize} kayıt`);
                
                // Database'i güncelle
                allData = convertedData;
                
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

// ===== DATE PICKER CALENDAR =====
let currentPickerMonth = new Date();

// Set the latest database date as default in the date input
function setDefaultDateToLatest() {
    const selectedDateInput = document.getElementById('selectedDate');
    if (selectedDateInput && !selectedDateInput.value && allData && allData.length > 0) {
        const dates = allData
            .filter(r => r.Tarih && /^\d{2}\.\d{2}\.\d{4}$/.test(r.Tarih))
            .map(r => {
                const [day, month, year] = r.Tarih.split('.');
                return { 
                    date: new Date(parseInt(year), parseInt(month) - 1, parseInt(day)),
                    str: r.Tarih 
                };
            })
            .sort((a, b) => b.date - a.date);
        
        if (dates.length > 0) {
            selectedDateInput.value = dates[0].str;
            console.log(`✅ Default date set to: ${dates[0].str}`);
        }
    }
}

function openDatePicker() {
    // Set calendar to show current month
    currentPickerMonth = new Date();
    currentPickerMonth.setHours(12, 0, 0, 0);  // Avoid timezone issues
    updateCalendarDisplay();
    
    // Ensure selectedDate input has a default value (latest database date)
    const selectedDateInput = document.getElementById('selectedDate');
    if (selectedDateInput && !selectedDateInput.value) {
        console.log(`🔍 selectedDate input boş, max tarih set ediliyor...`);
        
        // Get latest date from database (not today)
        if (allData && allData.length > 0) {
            // Find the latest date in database
            const dates = allData
                .filter(r => r.Tarih && /^\d{2}\.\d{2}\.\d{4}$/.test(r.Tarih))
                .map(r => {
                    const [day, month, year] = r.Tarih.split('.');
                    return { 
                        date: new Date(parseInt(year), parseInt(month) - 1, parseInt(day)),
                        str: r.Tarih 
                    };
                })
                .sort((a, b) => b.date - a.date);
            
            if (dates.length > 0) {
                const latestDateStr = dates[0].str;
                selectedDateInput.value = latestDateStr;
                console.log(`✓ selectedDate'a max tarih set: ${latestDateStr}`);
            }
        } else {
            console.warn(`⚠️ allData boş veya yüklenmemiş`);
        }
    }
    
    // Get latest date from database (for calendar month)
    let defaultDate = new Date();
    
    if (allData && allData.length > 0) {
        // Find the latest date in database
        const dates = allData
            .filter(r => r.Tarih && /^\d{2}\.\d{2}\.\d{4}$/.test(r.Tarih))
            .map(r => {
                const [day, month, year] = r.Tarih.split('.');
                return new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
            })
            .sort((a, b) => b - a);  // Sort descending
        
        if (dates.length > 0) {
            defaultDate = dates[0];  // Latest date
            console.log(`📅 Default tarih database'den alındı: ${defaultDate.toLocaleDateString('tr-TR')}`);
        }
    }
    
    // Set default as latest database date
    const day = String(defaultDate.getDate()).padStart(2, '0');
    const month = String(defaultDate.getMonth() + 1).padStart(2, '0');
    const year = defaultDate.getFullYear();
    const defaultFormatted = `${day}.${month}.${year}`;
    document.getElementById('selectedDate').value = defaultFormatted;
    
    document.getElementById('datePickerModal').style.display = 'flex';
}

function closeDatePicker() {
    document.getElementById('datePickerModal').style.display = 'none';
}

function prevCalendarMonth() {
    currentPickerMonth.setMonth(currentPickerMonth.getMonth() - 1);
    updateCalendarDisplay();
}

function nextCalendarMonth() {
    currentPickerMonth.setMonth(currentPickerMonth.getMonth() + 1);
    updateCalendarDisplay();
}

function updateCalendarDisplay() {
    const monthNames = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 
                       'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'];
    
    const year = currentPickerMonth.getFullYear();
    const month = currentPickerMonth.getMonth();
    
    // Update header
    document.getElementById('calendarMonthYear').textContent = `${monthNames[month]} ${year}`;
    
    // Generate calendar grid
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay());
    
    const grid = document.getElementById('calendarGrid');
    grid.innerHTML = '';
    
    // Day headers
    const dayHeaders = ['Paz', 'Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt'];
    dayHeaders.forEach(day => {
        const header = document.createElement('div');
        header.textContent = day;
        header.style.fontWeight = 'bold';
        header.style.textAlign = 'center';
        header.style.color = '#666';
        header.style.fontSize = '0.85em';
        grid.appendChild(header);
    });
    
    // Generate dates
    const currentDate = new Date(startDate);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    for (let i = 0; i < 42; i++) {
        // Create a copy of the date to avoid reference issues
        const cellDate = new Date(currentDate);
        
        const day = document.createElement('button');
        const dateNum = cellDate.getDate();
        const dateMonth = cellDate.getMonth();
        
        day.textContent = dateNum;
        day.style.padding = '8px';
        day.style.border = '1px solid #ddd';
        day.style.borderRadius = '4px';
        day.style.cursor = 'pointer';
        day.style.fontSize = '0.9em';
        day.style.background = '#fff';
        day.style.color = '#333';
        day.style.fontWeight = 'normal';
        
        // Check if this is today
        const dateToCheck = new Date(cellDate);
        dateToCheck.setHours(0, 0, 0, 0);
        const isToday = dateToCheck.getTime() === today.getTime();
        
        if (dateMonth !== month) {
            day.style.color = '#ccc';
            day.style.background = '#f5f5f5';
            day.disabled = true;
        } else if (isToday) {
            // Highlight today distinctly
            day.style.background = '#28a745';
            day.style.color = 'white';
            day.style.fontWeight = 'bold';
            day.style.border = '2px solid #1e7e34';
            day.style.boxShadow = '0 0 8px rgba(40, 167, 69, 0.5)';
            // Use cellDate copy, not currentDate
            day.onclick = () => selectDateFromPicker(new Date(cellDate));
        } else {
            // Use cellDate copy, not currentDate
            day.onclick = () => selectDateFromPicker(new Date(cellDate));
        }
        
        grid.appendChild(day);
        currentDate.setDate(currentDate.getDate() + 1);
    }
}

function selectDateFromPicker(date) {
    // Ensure date is not modified by reference issues
    const safeDate = new Date(date);
    safeDate.setHours(12, 0, 0, 0);
    
    const day = String(safeDate.getDate()).padStart(2, '0');
    const month = String(safeDate.getMonth() + 1).padStart(2, '0');
    const year = safeDate.getFullYear();
    const formattedDate = `${day}.${month}.${year}`;
    
    console.log(`📅 Seçilen tarih (Safe): ${formattedDate}`);
    document.getElementById('selectedDate').value = formattedDate;
    closeDatePicker();
    
    // Automatically apply filter with selected date
    setTimeout(() => {
        filterBySelectedDate();
    }, 100);
}

// ========== HANDS VIEWER ==========
function openHandsViewer(tournamentName) {
    const filteredResults = filterResults(database, 
        currentFilter.date || '', 
        currentFilter.tournament || tournamentName,
        currentFilter.player || '',
        currentFilter.minScore || 0,
        currentFilter.maxScore || 100
    );
    
    if (!filteredResults || filteredResults.length === 0) {
        alert(i18n[currentLanguage].noResults || 'No results found');
        return;
    }
    
    const firstRecord = filteredResults[0];
    if (!firstRecord.Hands) {
        alert(i18n[currentLanguage].noHands || 'Hands not available for this tournament');
        return;
    }
    
    showHandsModal(firstRecord.Hands, firstRecord.Turnuva);
}

function showHandsModal(hands, tournamentName) {
    let modal = document.getElementById('handsModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'handsModal';
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content" style="width: 95%; max-width: 1000px; max-height: 90vh; overflow-y: auto;">
                <span class="close" onclick="closeHandsModal()">&times;</span>
                <h2 id="handsTitle"></h2>
                <div id="handsGrid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-top: 20px;"></div>
            </div>
        `;
        document.body.appendChild(modal);
    }
    
    document.getElementById('handsTitle').textContent = tournamentName + ' - ' + (i18n[currentLanguage].hands || 'Hands');
    const grid = document.getElementById('handsGrid');
    grid.innerHTML = '';
    
    // Display hands for each board
    for (const [boardNum, boardHands] of Object.entries(hands)) {
        const boardDiv = document.createElement('div');
        boardDiv.className = 'board-card';
        boardDiv.style.cssText = `
            border: 2px solid #1e3c72;
            border-radius: 8px;
            padding: 15px;
            background: #f8f9fa;
            font-size: 12px;
            font-family: monospace;
        `;
        
        let handsHTML = `<strong>Board ${boardNum}</strong><br><br>`;
        for (const [direction, suit] of Object.entries(boardHands)) {
            let dirName = {N: 'North', S: 'South', E: 'East', W: 'West'}[direction];
            let cards = suit.S + ' ' + suit.H + ' ' + suit.D + ' ' + suit.C;
            handsHTML += `<div><strong>${dirName}:</strong> ${cards}</div>`;
        }
        
        boardDiv.innerHTML = handsHTML;
        grid.appendChild(boardDiv);
    }
    
    modal.style.display = 'block';
}

function closeHandsModal() {
    const modal = document.getElementById('handsModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function openHandsModal() {
    const modal = document.getElementById('handsModal');
    const content = document.getElementById('handsModalContent');
    
    if (!modal) return;
    
    // Load hands data
    const displayDate = window.dailyModalDate || window.selectedDate || '17.01.2026';
    fetch('/hands_database.json')
        .then(r => r.json())
        .then(data => {
            const hands = data.filter(h => h.date === displayDate);
            
            // Group by pair
            const pairMap = {};
            hands.forEach(h => {
                if (!pairMap[h.pair]) {
                    pairMap[h.pair] = { ns: [], ew: [] };
                }
                if (h.direction === 'NS') {
                    pairMap[h.pair].ns.push(h);
                } else {
                    pairMap[h.pair].ew.push(h);
                }
            });
            
            let html = `<style>
                @media print {
                    #handsModal { display: block !important; background: white !important; }
                    #handsModal > div { background: white !important; }
                    #handsModal > div > div { display: none; }
                    #handsModalContent { display: block !important; }
                    .hands-print-wrapper { display: block !important; }
                    .hands-pair-group { page-break-inside: avoid; break-inside: avoid; }
                    .hands-card { page-break-inside: avoid; break-inside: avoid; }
                    .print-button { display: none; }
                    .export-button { display: none; }
                    .hands-card a { display: none !important; }
                }
            </style>
            <div class="hands-print-wrapper">
                <div style="text-align: center; margin-bottom: 20px; print:display:none;">
                    <p style="font-size: 1.1rem; color: #28a745;">✓ ${hands.length} el, ${Object.keys(pairMap).length} çift</p>
                    <button onclick="window.print()" class="print-button" style="padding: 8px 20px; background: #28a745; color: white; border: none; border-radius: 3px; cursor: pointer; font-weight: bold; margin-right: 10px;">🖨️ Yazdır</button>
                    <button onclick="downloadHands27()" class="export-button" style="padding: 8px 20px; background: #17a2b8; color: white; border: none; border-radius: 3px; cursor: pointer; font-weight: bold;">⬇️ İndir (TXT)</button>
                </div>`;
            
            Object.keys(pairMap).sort().forEach(pairName => {
                const pairData = pairMap[pairName];
                const allBoards = [...pairData.ns, ...pairData.ew];
                
                html += `<div class="hands-pair-group" style="margin-bottom: 30px; background: #f9f9f9; padding: 20px; border-radius: 8px; border-left: 4px solid #1e3c72;">
                    <h3 style="color: #1e3c72; margin: 0 0 15px 0; font-size: 1.1em;">👥 ${pairName}</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px;">`;
                
                allBoards.forEach(h => {
                    const dealerLetters = ['N', 'E', 'S', 'W'];
                    const dealerLetter = dealerLetters[(h.board - 1) % 4];
                    const dealerMap = {'N':'1','E':'2','S':'3','W':'4'};
                    const vulnMap = {'None':'0','NS':'1','EW':'2','Both':'3'};
                    const d = dealerMap[dealerLetter] || '1';
                    const v = vulnMap[h.vulnerability] || '0';
                    
                    // Get hands with rotation based on dealer
                    const mappedFields = getMappedHands(h, dealerLetter);
                    
                    // Convert hand string to LIN format (Spades.Hearts.Diamonds.Clubs)
                    const hands = {
                        'N': `S${mappedFields.N.split('.')[0]}H${mappedFields.N.split('.')[1]}D${mappedFields.N.split('.')[2]}C${mappedFields.N.split('.')[3]}`,
                        'E': `S${mappedFields.E.split('.')[0]}H${mappedFields.E.split('.')[1]}D${mappedFields.E.split('.')[2]}C${mappedFields.E.split('.')[3]}`,
                        'S': `S${mappedFields.S.split('.')[0]}H${mappedFields.S.split('.')[1]}D${mappedFields.S.split('.')[2]}C${mappedFields.S.split('.')[3]}`,
                        'W': `S${mappedFields.W.split('.')[0]}H${mappedFields.W.split('.')[1]}D${mappedFields.W.split('.')[2]}C${mappedFields.W.split('.')[3]}`
                    };
                    
                    // Order hands starting from dealer, but only output 3 hands (BBO calculates 4th)
                    const dealerOrder = {'N': ['N', 'E', 'S'], 'E': ['E', 'S', 'W'], 'S': ['S', 'W', 'N'], 'W': ['W', 'N', 'E']};
                    const orderedHands = dealerOrder[dealerLetter] || ['N', 'E', 'S'];
                    const handString = orderedHands.map(pos => hands[pos]).join(',');
                    
                    const lin = `qx|o1|md|${d}${handString},|rh||ah|Board ${h.board}|sv|${v}|pg||`;
                    const url = `https://www.bridgebase.com/tools/handviewer.html?lin=${encodeURIComponent(lin)}`;
                    const iframeUrl = `https://www.bridgebase.com/tools/handviewer.html?bbo=y&lin=${encodeURIComponent(lin)}`;
                    
                    const borderColor = h.direction === 'NS' ? '#007bff' : '#dc3545';
                    
                    let ddTableHtml = '';
                    if (h.dd_analysis && Object.keys(h.dd_analysis).length > 0) {
                        ddTableHtml = `<div style="margin-top: 10px; border-top: 1px solid #ddd; padding-top: 10px;">
                            <table style="width: 100%; border-collapse: collapse; font-size: 0.75rem; font-family: monospace;">
                                <tr style="background: #f5f5f5;">
                                    <td style="border: 1px solid #ccc; padding: 3px; text-align: center; width: 20%;"></td>
                                    <td style="border: 1px solid #ccc; padding: 3px; text-align: center; width: 20%; font-weight: bold;">♠</td>
                                    <td style="border: 1px solid #ccc; padding: 3px; text-align: center; width: 20%; font-weight: bold;">♥</td>
                                    <td style="border: 1px solid #ccc; padding: 3px; text-align: center; width: 20%; font-weight: bold;">♦</td>
                                    <td style="border: 1px solid #ccc; padding: 3px; text-align: center; width: 20%; font-weight: bold;">NT</td>
                                </tr>
                                <tr>
                                    <td style="border: 1px solid #ccc; padding: 3px; text-align: center; font-weight: bold;">N</td>
                                    <td style="border: 1px solid #ccc; padding: 3px; text-align: center;">${h.dd_analysis['SN'] || '-'}</td>
                                    <td style="border: 1px solid #ccc; padding: 3px; text-align: center;">${h.dd_analysis['HN'] || '-'}</td>
                                    <td style="border: 1px solid #ccc; padding: 3px; text-align: center;">${h.dd_analysis['DN'] || '-'}</td>
                                    <td style="border: 1px solid #ccc; padding: 3px; text-align: center;">${h.dd_analysis['NTN'] || '-'}</td>
                                </tr>
                                <tr>
                                    <td style="border: 1px solid #ccc; padding: 3px; text-align: center; font-weight: bold;">S</td>
                                    <td style="border: 1px solid #ccc; padding: 3px; text-align: center;">${h.dd_analysis['SS'] || '-'}</td>
                                    <td style="border: 1px solid #ccc; padding: 3px; text-align: center;">${h.dd_analysis['HS'] || '-'}</td>
                                    <td style="border: 1px solid #ccc; padding: 3px; text-align: center;">${h.dd_analysis['DS'] || '-'}</td>
                                    <td style="border: 1px solid #ccc; padding: 3px; text-align: center;">${h.dd_analysis['NTS'] || '-'}</td>
                                </tr>
                                <tr>
                                    <td style="border: 1px solid #ccc; padding: 3px; text-align: center; font-weight: bold;">E</td>
                                    <td style="border: 1px solid #ccc; padding: 3px; text-align: center;">${h.dd_analysis['SE'] || '-'}</td>
                                    <td style="border: 1px solid #ccc; padding: 3px; text-align: center;">${h.dd_analysis['HE'] || '-'}</td>
                                    <td style="border: 1px solid #ccc; padding: 3px; text-align: center;">${h.dd_analysis['DE'] || '-'}</td>
                                    <td style="border: 1px solid #ccc; padding: 3px; text-align: center;">${h.dd_analysis['NTE'] || '-'}</td>
                                </tr>
                                <tr>
                                    <td style="border: 1px solid #ccc; padding: 3px; text-align: center; font-weight: bold;">W</td>
                                    <td style="border: 1px solid #ccc; padding: 3px; text-align: center;">${h.dd_analysis['SW'] || '-'}</td>
                                    <td style="border: 1px solid #ccc; padding: 3px; text-align: center;">${h.dd_analysis['HW'] || '-'}</td>
                                    <td style="border: 1px solid #ccc; padding: 3px; text-align: center;">${h.dd_analysis['DW'] || '-'}</td>
                                    <td style="border: 1px solid #ccc; padding: 3px; text-align: center;">${h.dd_analysis['NTW'] || '-'}</td>
                                </tr>
                            </table>
                        </div>`;
                    }
                    
                    html += `<div class="hands-card" style="background: white; padding: 12px; border-radius: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.1); border-left: 4px solid ${borderColor}; page-break-inside: avoid;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <h4 style="margin: 0; color: ${borderColor}; font-size: 1rem;">Tahta ${h.board}</h4>
                            <span style="background: ${borderColor}; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.8em; font-weight: bold;">${h.direction}</span>
                        </div>
                        <p style="font-size: 0.85rem; color: #666; margin: 5px 0;"><strong>Dealer:</strong> ${dealerLetter} | <strong>Vuln:</strong> ${h.vulnerability}</p>
                        <p style="font-size: 0.85rem; color: #666; margin: 5px 0;"><strong>Score:</strong> ${h.score.toFixed(2)}</p>
                        <div style="background: #f5f5f5; padding: 8px; margin: 8px 0; border-radius: 3px; font-family: monospace; font-size: 0.8rem; line-height: 1.4; page-break-inside: avoid;">
                            <div>♠ ${h.N}</div>
                            <div>♥ ${h.S}</div>
                            <div>♦ ${h.E}</div>
                        </div>
                        ${ddTableHtml}
                        <a href="${url}" target="_blank" style="display: inline-block; padding: 6px 12px; background: #007bff; color: white; text-decoration: none; border-radius: 3px; font-size: 0.85rem; margin-top: 8px;">🔗 BBO</a>
                    </div>`;
                });
                
                html += '</div></div>';
            });
            
            html += '</div>';
            content.innerHTML = html;
            modal.style.display = 'block';
        })
        .catch(e => {
            content.innerHTML = `<p style="color: red;">Hata: ${e.message}</p>`;
            modal.style.display = 'block';
        });
}

function downloadHands27() {
    const textDate = window.dailyModalDate || window.selectedDate || '17.01.2026';
    fetch('/hands_database.json')
        .then(r => r.json())
        .then(data => {
            const hands = data.filter(h => h.date === textDate).sort((a, b) => a.board - b.board);
            
            let txt = '═══════════════════════════════════════════════════════════════════\n';
            txt += `                   ${textDate} TÜM ELLERİ (${hands.length} TAHTA)\n`;
            txt += '═══════════════════════════════════════════════════════════════════\n\n';
            
            hands.forEach((h, idx) => {
                txt += `TAHTA ${h.board}\n`;
                txt += `───────────────────────────────────────────────────────────────────\n`;
                txt += `Çift: ${h.pair} | Yön: ${h.direction} | Score: ${h.score.toFixed(2)}\n`;
                txt += `Dealer: ${dealerLetter} | Vuln: ${h.vulnerability}\n`;
                txt += `\n`;
                txt += `  ♠ NORTH (Kuzey):\n`;
                txt += `    ${h.N}\n`;
                txt += `\n`;
                txt += `  ♥ SOUTH (Güney):\n`;
                txt += `    ${h.S}\n`;
                txt += `\n`;
                txt += `  ♦ EAST (Doğu):\n`;
                txt += `    ${h.E}\n`;
                txt += `\n`;
                txt += `  ♣ WEST (Batı):\n`;
                txt += `    ${h.W}\n`;
                txt += `\n`;
                
                // DD Table
                if (h.dd_analysis && Object.keys(h.dd_analysis).length > 0) {
                    txt += `  📊 DOUBLE DUMMY ANALYSIS (Trick Sayıları):\n`;
                    txt += `\n`;
                    txt += `     NT   ♠   ♥   ♦   ♣\n`;
                    txt += `    ─────────────────────\n`;
                    
                    const seats = ['N', 'E', 'S', 'W'];
                    seats.forEach(seat => {
                        const nt = h.dd_analysis[`NT${seat}`] || '-';
                        const s = h.dd_analysis[`S${seat}`] || '-';
                        const h_suit = h.dd_analysis[`H${seat}`] || '-';
                        const d = h.dd_analysis[`D${seat}`] || '-';
                        const c = h.dd_analysis[`C${seat}`] || '-';
                        txt += `  ${seat}:   ${String(nt).padStart(2)}  ${String(s).padStart(2)}  ${String(h_suit).padStart(2)}  ${String(d).padStart(2)}  ${String(c).padStart(2)}\n`;
                    });
                    txt += `\n`;
                }
                
                // LIN for BBO
                const dealerLetters = ['N', 'E', 'S', 'W'];
                const dealerLetter = dealerLetters[(h.board - 1) % 4];
                const dealerMap = {'N':'1','E':'2','S':'3','W':'4'};
                const vulnMap = {'None':'0','NS':'1','EW':'2','Both':'3'};
                const d = dealerMap[dealerLetter] || '1';
                const v = vulnMap[h.vulnerability] || '0';
                
                // Get hands with rotation based on dealer
                const mappedHandsLIN = getMappedHands(h, dealerLetter);
                
                // Convert hand string to LIN format (Spades.Hearts.Diamonds.Clubs)
                const handsLIN = {
                    'N': `S${mappedHandsLIN.N.split('.')[0]}H${mappedHandsLIN.N.split('.')[1]}D${mappedHandsLIN.N.split('.')[2]}C${mappedHandsLIN.N.split('.')[3]}`,
                    'E': `S${mappedHandsLIN.E.split('.')[0]}H${mappedHandsLIN.E.split('.')[1]}D${mappedHandsLIN.E.split('.')[2]}C${mappedHandsLIN.E.split('.')[3]}`,
                    'S': `S${mappedHandsLIN.S.split('.')[0]}H${mappedHandsLIN.S.split('.')[1]}D${mappedHandsLIN.S.split('.')[2]}C${mappedHandsLIN.S.split('.')[3]}`,
                    'W': `S${mappedHandsLIN.W.split('.')[0]}H${mappedHandsLIN.W.split('.')[1]}D${mappedHandsLIN.W.split('.')[2]}C${mappedHandsLIN.W.split('.')[3]}`
                };
                
                // Order hands starting from dealer, but only output 3 hands (BBO calculates 4th)
                const dealerOrder = {'N': ['N', 'E', 'S'], 'E': ['E', 'S', 'W'], 'S': ['S', 'W', 'N'], 'W': ['W', 'N', 'E']};
                const orderedHandsLIN = dealerOrder[h.dealer] || ['N', 'E', 'S'];
                const handStringLIN = orderedHandsLIN.map(pos => handsLIN[pos]).join(',');
                const lin = `qx|o1|md|${d}${handStringLIN},|rh||ah|Board ${h.board}|sv|${v}|pg||`;
                
                txt += `BBO Link:\n`;
                txt += `https://www.bridgebase.com/tools/handviewer.html?lin=${encodeURIComponent(lin)}\n`;
                txt += `\n`;
                txt += `═══════════════════════════════════════════════════════════════════\n\n`;
            });
            
            txt += `ÖZET:\n`;
            txt += `Toplam: ${hands.length} el\n`;
            txt += `Tarih: 17.01.2026\n`;
            txt += `Dışa aktarma: ${new Date().toLocaleString('tr-TR')}\n`;
            
            // Download
            const blob = new Blob([txt], { type: 'text/plain; charset=utf-8' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = '27_Tahta_17_01_2026.txt';
            link.click();
        })
        .catch(e => alert('Hata: ' + e.message));
}

function createHandCard(h) {
    const dealerLetters = ['N', 'E', 'S', 'W'];
    const dealerLetter = dealerLetters[(h.board - 1) % 4];
    const dealerMap = {'N':'1','E':'2','S':'3','W':'4'};
    const vulnMap = {'None':'0','NS':'1','EW':'2','Both':'3'};
    const d = dealerMap[dealerLetter] || '1';
    const v = vulnMap[h.vulnerability] || '0';
    
    console.log('createHandCard called with:', {board: h.board, dd_analysis: h.dd_analysis, hasDD: h.dd_analysis && Object.keys(h.dd_analysis).length > 0});
    
    // Get hands with rotation based on dealer
    const mappedHandsCard = getMappedHands(h, dealerLetter);
    
    // Convert hand string to LIN format (Spades.Hearts.Diamonds.Clubs)
    const handsLIN = {
        'N': `S${mappedHandsCard.N.split('.')[0]}H${mappedHandsCard.N.split('.')[1]}D${mappedHandsCard.N.split('.')[2]}C${mappedHandsCard.N.split('.')[3]}`,
        'E': `S${mappedHandsCard.E.split('.')[0]}H${mappedHandsCard.E.split('.')[1]}D${mappedHandsCard.E.split('.')[2]}C${mappedHandsCard.E.split('.')[3]}`,
        'S': `S${mappedHandsCard.S.split('.')[0]}H${mappedHandsCard.S.split('.')[1]}D${mappedHandsCard.S.split('.')[2]}C${mappedHandsCard.S.split('.')[3]}`,
        'W': `S${mappedHandsCard.W.split('.')[0]}H${mappedHandsCard.W.split('.')[1]}D${mappedHandsCard.W.split('.')[2]}C${mappedHandsCard.W.split('.')[3]}`
    };
    
    // Order hands starting from dealer, but only output 3 hands (BBO calculates 4th)
    const dealerOrder = {'N': ['N', 'E', 'S'], 'E': ['E', 'S', 'W'], 'S': ['S', 'W', 'N'], 'W': ['W', 'N', 'E']};
    const orderedHandsLIN = dealerOrder[dealerLetter] || ['N', 'E', 'S'];
    const handStringLIN = orderedHandsLIN.map(pos => handsLIN[pos]).join(',');
    
    const lin = `qx|o1|md|${d}${handStringLIN},|rh||ah|Board ${h.board}|sv|${v}|pg||`;
    const iframeUrl = `https://www.bridgebase.com/tools/handviewer.html?lin=${encodeURIComponent(lin)}`;
    
    // DD table disabled - removed from modal display
    let ddTableHtml = '';
    
    return `<div style="background: white; padding: 12px; border-radius: 4px; box-sizing: border-box;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; font-size: 0.85rem; color: #666;">
            <span><strong>Dealer:</strong> ${dealerLetter}</span>
            <span style="font-weight: bold; color: #1e3c72;">Board ${h.board}</span>
            <span><strong>Vuln:</strong> ${h.vulnerability}</span>
        </div>
        
        <iframe src="${iframeUrl}" style="width: 100%; height: 320px; border: 1px solid #ddd; border-radius: 4px;"></iframe>
    </div>`;
}


// ===== PAIR SUMMARY MODAL =====
// Shows board-by-board results for a pair including contract and declarer info

async function openPairSummaryModal(eventId, pairNum, direction, pairNames) {
    console.log(`📋 Opening pair summary: event=${eventId}, pair=${pairNum}, direction=${direction}`);
    
    // Open dedicated pair summary page instead of modal
    const url = `pair_summary.html?event=${eventId}&pair=${pairNum}&direction=${direction}&names=${encodeURIComponent(pairNames || '')}`;
    window.open(url, '_blank');
}

function closePairSummaryModal() {
    // Not needed anymore, but keep for compatibility
    const modal = document.getElementById('pairSummaryModal');
    if (modal) {
        modal.remove();
        document.body.style.overflow = 'auto';
    }
}

// Helper to extract event ID from tournament link
function extractEventIdFromLink(link) {
    if (!link) return null;
    const match = link.match(/event=(\d+)/);
    return match ? match[1] : null;
}

// Make function globally available
window.openPairSummaryModal = openPairSummaryModal;
window.closePairSummaryModal = closePairSummaryModal;

// Global event delegation for clickable pairs - works even for dynamically added elements
document.addEventListener('click', function(e) {
    const clickablePair = e.target.closest('.clickable-pair');
    if (clickablePair) {
        const eventId = clickablePair.dataset.event;
        const pairNum = clickablePair.dataset.pair;
        const direction = clickablePair.dataset.direction;
        const names = clickablePair.dataset.names;
        
        console.log('🖱️ Clicked pair:', { eventId, pairNum, direction, names });
        
        if (eventId && eventId !== 'null' && eventId !== '') {
            openPairSummaryModal(eventId, pairNum, direction, names);
        } else {
            console.log('⚠️ No eventId found for this pair');
        }
    }
});

