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

function selectPlayerName(playerName) {
    const playerInput = document.getElementById('playerName');
    const dropdown = document.getElementById('playerNameSuggestions');
    
    playerInput.value = playerName;
    dropdown.style.display = 'none';
    
    console.log(`Seçilen oyuncu: ${playerName}`);
    // Gerekirse oyuncunun sonuçlarını göstermek için buraya kod eklenebilir
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
    
    showPlayerTab(1);
}

function closePlayerModal() {
    document.getElementById('playerModal').style.display = 'none';
    window.playerModalData = null;
}

function showPlayerTab(tabNum) {
    console.log('showPlayerTab çağırıldı:', tabNum);
    
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
    if (pageIndicator) pageIndicator.textContent = `Sayfa ${tabNum}/2`;
    if (prevBtn) prevBtn.style.visibility = tabNum > 1 ? 'visible' : 'hidden';
    if (nextBtn) nextBtn.style.visibility = tabNum < 2 ? 'visible' : 'hidden';
    
    if (tabNum === 1) {
        // İstatistikler sayfası
        if (title) title.textContent = 'Oyuncu İstatistikleri';
        
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
        
        let html = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:15px;">';
        html += '<div style="background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);border-radius:12px;padding:20px;color:white;display:flex;flex-direction:column;justify-content:center;align-items:center;aspect-ratio:1/1;">';
        html += '<div style="font-size:0.75em;opacity:0.9;margin-bottom:10px;">🎯 Oynadığı Maç</div>';
        html += '<div style="font-size:1.8em;font-weight:bold;line-height:1;">' + playCount + '</div></div>';
        
        html += '<div style="background:linear-gradient(135deg, #f093fb 0%, #f5576c 100%);border-radius:12px;padding:20px;color:white;display:flex;flex-direction:column;justify-content:center;align-items:center;aspect-ratio:1/1;">';
        html += '<div style="font-size:0.75em;opacity:0.9;margin-bottom:10px;">🥇 1. Olduğu Maç</div>';
        html += '<div style="font-size:1.8em;font-weight:bold;line-height:1;">' + firstPlaceCount + '</div></div>';
        
        html += '<div style="background:linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);border-radius:12px;padding:20px;color:white;display:flex;flex-direction:column;justify-content:center;align-items:center;aspect-ratio:1/1;">';
        html += '<div style="font-size:0.75em;opacity:0.9;margin-bottom:10px;">📊 Skor Ortalaması</div>';
        html += '<div style="font-size:1.8em;font-weight:bold;line-height:1;">% ' + avgScore + '</div></div>';
        
        html += '<div style="background:linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);border-radius:12px;padding:20px;color:white;display:flex;flex-direction:column;justify-content:center;align-items:center;aspect-ratio:1/1;">';
        html += '<div style="font-size:0.75em;opacity:0.9;margin-bottom:10px;">👥 Farklı Partner</div>';
        html += '<div style="font-size:1.8em;font-weight:bold;line-height:1;">' + uniquePartners + '</div></div>';
        html += '</div>';
        
        html += '<div style="margin-top:30px;display:grid;grid-template-columns:1fr 1fr;gap:15px;">';
        
        html += '<div style="background:#f8f9ff;border:2px solid #667eea;border-radius:12px;padding:20px;display:flex;flex-direction:column;justify-content:center;align-items:center;min-height:140px;text-align:center;">';
        html += '<div style="font-size:0.9em;color:#666;margin-bottom:12px;font-weight:bold;">🤝 En Çok Oynadığı Partner</div>';
        html += '<div style="font-size:1.3em;font-weight:bold;color:#1e3c72;margin-bottom:8px;">' + (topPartner ? topPartner[0] : 'N/A') + '</div>';
        html += '<div style="background:#667eea;color:white;padding:8px 12px;border-radius:6px;text-align:center;font-weight:bold;width:100%;">' + (topPartner ? topPartner[1] + ' kez' : '-') + '</div>';
        html += '</div>';
        
        html += '<div style="background:#fff8f9;border:2px solid #f5576c;border-radius:12px;padding:20px;display:flex;flex-direction:column;justify-content:center;align-items:center;min-height:140px;text-align:center;">';
        html += '<div style="font-size:0.9em;color:#666;margin-bottom:12px;font-weight:bold;">⭐ En İyi Skoru Yaptığı Partner</div>';
        html += '<div style="font-size:1.3em;font-weight:bold;color:#1e3c72;margin-bottom:8px;">' + (bestPartner ? bestPartner[0] : 'N/A') + '</div>';
        html += '<div style="background:#f5576c;color:white;padding:8px 12px;border-radius:6px;text-align:center;font-weight:bold;width:100%;">% ' + (bestPartner ? bestPartner[1].score.toFixed(2) : '-') + '</div>';
        html += '</div>';
        html += '</div>';
        
        content.innerHTML = html;
        console.log('Tab 1 HTML render edildi');
    } else if (tabNum === 2) {
        // Sonuçlar sayfası
        const recordCount = data.length;
        if (title) {
            title.style.fontSize = '1.1em';
            title.textContent = 'Turnuvalar & Sonuçları (' + recordCount + ' tur)';
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
        
        const getSortIcon = (sortBy) => {
            if (window.playerSortConfig && window.playerSortConfig.sortBy === sortBy) {
                return window.playerSortConfig.order === 'asc' ? '▲' : '▼';
            }
            return '↕';
        };
        
        let html = '<div style="background:linear-gradient(135deg, #f5f7ff 0%, #f0f2ff 100%);border-radius:12px;padding:12px;overflow-x:auto;">';
        html += '<table style="width:100%;border-collapse:separate;border-spacing:0;font-size:0.9em;border-radius:8px;overflow:hidden;">';
        html += '<thead style="background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);color:white;">';
        html += '<tr><th style="padding:12px 4px;text-align:center;cursor:pointer;font-weight:bold;border:none;width:25px;" onclick="togglePlayerSort(\'date\')">';
        html += '<div style="display:flex;align-items:center;justify-content:center;gap:1px;font-size:0.65em;flex-wrap:wrap;line-height:1.2;">📅 Tarih <span style="font-size:0.9em;font-weight:bold;">' + getSortIcon('date') + '</span></div>';
        html += '</th><th style="padding:12px 10px;text-align:left;font-weight:bold;border:none;flex:1;">';
        html += '<div style="display:flex;align-items:center;gap:4px;font-size:0.9em;">🤝 Partner</div></th>';
        html += '<th style="padding:12px 4px;text-align:center;cursor:pointer;font-weight:bold;border:none;width:25px;" onclick="togglePlayerSort(\'score\')">';
        html += '<div style="display:flex;align-items:center;justify-content:center;gap:1px;font-size:0.65em;flex-wrap:wrap;line-height:1.2;">📊 Skor <span style="font-size:0.9em;font-weight:bold;">' + getSortIcon('score') + '</span></div>';
        html += '</th></tr></thead><tbody>';
        
        sorted.forEach((row, idx) => {
            // Tarih formatını dd.mm.yy yaparak göster
            const tarihParts = row['Tarih'].split('.');
            const dateFmt = tarihParts[0] + '.' + tarihParts[1] + '.' + (tarihParts[2].length > 2 ? tarihParts[2].slice(-2) : tarihParts[2]);
            
            // Partner bulurken normalize et (Türkçe karakterleri de)
            const oyuncu1Norm = normalizeText(row['Oyuncu 1'].trim().replace(/\s+/g, ' '));
            const oyuncu2Norm = normalizeText(row['Oyuncu 2'].trim().replace(/\s+/g, ' '));
            const partner = oyuncu1Norm === playerName ? row['Oyuncu 2'] : row['Oyuncu 1'];
            const score = parseFloat(row['Skor']);
            
            // Score'a göre renk: 50+ yeşil, <50 kırmızı
            const scoreColor = score >= 50 ? '#16a34a' : '#dc2626';
            
            const isFirstRow = idx === 0;
            const isLastRow = idx === sorted.length - 1;
            const borderRadius = (isFirstRow ? 'border-radius:8px 8px 0 0;' : '') + (isLastRow ? 'border-radius:0 0 8px 8px;' : '');
            
            html += '<tr style="' + borderRadius + 'background:linear-gradient(90deg, rgba(102,126,234,0.05) 0%, rgba(118,75,162,0.05) 100%);';
            html += 'border-bottom:1px solid rgba(102,126,234,0.15);transition:all 0.3s ease;cursor:pointer;box-shadow:0 2px 0 rgba(0,0,0,0.02);" ';
            html += 'onmouseover="this.style.background=\'linear-gradient(90deg, rgba(102,126,234,0.15) 0%, rgba(118,75,162,0.15) 100%)\';this.style.boxShadow=\'0 4px 8px rgba(102,126,234,0.2)\';" ';
            html += 'onmouseout="this.style.background=\'linear-gradient(90deg, rgba(102,126,234,0.05) 0%, rgba(118,75,162,0.05) 100%)\';this.style.boxShadow=\'0 2px 0 rgba(0,0,0,0.02)\';">';
            html += '<td style="padding:10px 4px;text-align:center;font-weight:bold;color:#1e3c72;width:25px;font-size:0.65em;">' + dateFmt + '</td>';
            html += '<td style="padding:10px 10px;text-align:center;color:#334155;flex:1;font-weight:500;letter-spacing:0.3px;">' + partner + '</td>';
            html += '<td style="padding:10px 4px;text-align:center;font-weight:bold;color:' + scoreColor + ';font-size:0.75em;width:25px;">% ' + score.toFixed(2) + '</td>';
            html += '</tr>';
        });
        
        html += '</tbody></table></div>';
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

// ===== QUICK DATE FILTER BUTTON HANDLER =====
function setDateRangeFilter(period, event) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    if (!databaseReady) {
        alert('Veritabanı henüz yüklenmedi');
        return;
    }
    
    window.period = period;
    
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
    
    // Tarihe göre filtrele
    const filtered = allData.filter(record => {
        const [day, month, year] = record.Tarih.split('.').map(Number);
        const d = new Date(year, month - 1, day);
        return d >= startDate && d <= endDate;
    });
    
    // Yeni 3-sayfalı modal'ı aç
    openGlobalRangeModal(filtered, period);
}

// ===== EXCEL EXPORT FUNCTION =====
function exportResultsToExcel(results) {
    if (!results || results.length === 0) {
        alert('Dışa aktarılacak veri yok!');
        return;
    }
    
    // Veri hazırlama
    const exportData = results.map(row => ({
        'Tarih': row['Tarih'] || '-',
        'Sıra': row['Sıra'] || '-',
        'Oyuncular': `${row['Oyuncu 1']} - ${row['Oyuncu 2']}` || '-',
        '% Skor': row['Skor'] || '-',
        'Yön': row['type'] === 'NS' ? 'Kuzey-Güney' : 'Doğu-Batı'
    }));
    
    // Workbook ve worksheet oluştur
    const worksheet = XLSX.utils.json_to_sheet(exportData);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Turnuva Sonuçları');
    
    // Sütun genişliklerini ayarla
    const columnWidths = [
        { wch: 15 },  // Tarih
        { wch: 8 },   // Sıra
        { wch: 35 },  // Oyuncular
        { wch: 12 },  // % Skor
        { wch: 15 }   // Yön
    ];
    worksheet['!cols'] = columnWidths;
    
    // Header stilini uygula
    const headerRow = worksheet['1'];
    for (let col in headerRow) {
        if (col !== '!ref' && col !== '!merged') {
            headerRow[col].s = {
                fill: { fgColor: { rgb: 'FF667EEA' } },
                font: { bold: true, color: { rgb: 'FFFFFFFF' } },
                alignment: { horizontal: 'center', vertical: 'center' }
            };
        }
    }
    
    // Excel dosyasını indir
    const fileName = `Turnuva_Sonuclari_${new Date().toLocaleDateString('tr-TR').replace(/\./g, '_')}.xlsx`;
    XLSX.writeFile(workbook, fileName);
}

// ===== MOBILE MODAL PAGE NAVIGATION =====
const MOBILE_TOTAL_PAGES = 2;

function updateMobileNav(page) {
    const totalSpan = document.getElementById('totalPages');
    if (totalSpan) totalSpan.textContent = MOBILE_TOTAL_PAGES;

    const currentPageSpan = document.getElementById('currentPage');
    if (currentPageSpan) currentPageSpan.textContent = page;

    const prevBtn = document.querySelector('#resultsNavigation button:first-child');
    const nextBtn = document.querySelector('#resultsNavigation button:last-child');
    if (prevBtn) prevBtn.style.visibility = page > 1 ? 'visible' : 'hidden';
    if (nextBtn) nextBtn.style.visibility = page < MOBILE_TOTAL_PAGES ? 'visible' : 'hidden';
    
    // Modal başlığını sayfa numarasına göre güncelle
    const headerLabel = document.getElementById('modalHeaderLabel');
    if (headerLabel) {
        if (page === 1) headerLabel.textContent = '� İstatistikler';
        else if (page === 2) headerLabel.textContent = '🏆 Turnuva Sonuçları';
    }
}

function goToNextPage() {
    console.log('goToNextPage button clicked');
    const pagesContainer = document.getElementById('pagesContainer');
    const currentPageEl = document.getElementById('currentPage');
    
    if (!pagesContainer || !currentPageEl) {
        console.error('Missing elements!');
        return;
    }
    
    let page = parseInt(currentPageEl.textContent, 10) || 1;
    console.log('Current page:', page);
    
    if (page < MOBILE_TOTAL_PAGES) {
        page++;
        const translatePercent = ((page - 1) / MOBILE_TOTAL_PAGES) * 100;
        const newTransform = `translateX(-${translatePercent}%)`;
        console.log('Moving to page:', page, 'Transform:', newTransform);
        pagesContainer.style.transform = newTransform;
        currentPageEl.textContent = page;
    }
    updateMobileNav(page);
}

function goToPreviousPage() {
    const pagesContainer = document.getElementById('pagesContainer');
    const currentPageEl = document.getElementById('currentPage');
    const totalPagesEl = document.getElementById('totalPages');
    
    if (!pagesContainer || !currentPageEl || !totalPagesEl) return;
    
    let page = parseInt(currentPageEl.textContent, 10) || 1;
    let totalPages = parseInt(totalPagesEl.textContent, 10) || 2;
    
    if (page > 1) {
        page--;
        const translatePercent = ((page - 1) / totalPages) * 100;
        pagesContainer.style.transform = `translateX(-${translatePercent}%)`;
        currentPageEl.textContent = page;
        
        // Update nav based on total pages
        if (totalPages === 3) {
            updateDailyNav(page);
        } else {
            updateMobileNav(page);
        }
    }
}

function goToNextPage() {
    const pagesContainer = document.getElementById('pagesContainer');
    const currentPageEl = document.getElementById('currentPage');
    const totalPagesEl = document.getElementById('totalPages');
    
    if (!pagesContainer || !currentPageEl || !totalPagesEl) return;
    
    let page = parseInt(currentPageEl.textContent, 10) || 1;
    let totalPages = parseInt(totalPagesEl.textContent, 10) || 2;
    
    if (page < totalPages) {
        page++;
        const translatePercent = ((page - 1) / totalPages) * 100;
        pagesContainer.style.transform = `translateX(-${translatePercent}%)`;
        currentPageEl.textContent = page;
        
        // Update nav based on total pages
        if (totalPages === 3) {
            updateDailyNav(page);
        } else {
            updateMobileNav(page);
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
    // Tarih seç inputuna bir önceki günü varsayılan olarak ata (yerel saat)
    const selectedDateInput = document.getElementById('selectedDate');
    if (selectedDateInput) {
        const now = new Date();
        const localYesterday = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1);
        const yyyy = localYesterday.getFullYear();
        const mm = String(localYesterday.getMonth() + 1).padStart(2, '0');
        const dd = String(localYesterday.getDate()).padStart(2, '0');
        selectedDateInput.value = `${yyyy}-${mm}-${dd}`;
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
function loadDatabase() {
    // Varsayılan değerler
    let period = window.period || 'since2020';
    let today = new Date();
    let startDate, endDate;
    let content = document.getElementById('globalModalContent');
    if (!content) return;
    // 1. sayfa: Günün Şampiyonları (NS/EW kutulu)
    content.innerHTML = `<h2 style="text-align:center;color:#1e3c72;margin:16px 0 20px 0;font-size:1.2em;">👑 Günün Şampiyonları</h2><div id="statsGrid"></div>`;
    displayChampions(globalModalData);
    const footer = document.getElementById('globalNavFooter');
    if (footer) {
        footer.style.display = 'flex';
        footer.innerHTML = `<button onclick="goToGlobalPage(-1, event)" style="flex:1;padding:10px;background:#17a2b8;color:white;border:none;cursor:pointer;margin:5px;">← Önceki</button><div style="flex:1;text-align:center;padding:10px;background:#f0f0f0;margin:5px;border-radius:4px;">Sayfa 1/3</div><button onclick="goToGlobalPage(1, event)" style="flex:1;padding:10px;background:#1e3c72;color:white;border:none;cursor:pointer;margin:5px;">Sonraki →</button>`;
    }
    // Sabit tarih aralıkları
    if (period === 'currentMonth') {
        // Bu Ay: Bugünkü ay ve yıl
        const currentMonth = today.getMonth();
        const currentYear = today.getFullYear();
        startDate = new Date(currentYear, currentMonth, 1);
        endDate = new Date(currentYear, currentMonth + 1, 0); // Ayın son günü
    } else if (period === 'currentYear') {
        // Bu Yıl: 01.01.bugünYılı - 31.12.bugünYılı (her zaman yıl sonu)
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

    const startStr = formatDate(startDate);
    const endStr = formatDate(endDate);

    console.log(`🔍 Filter: ${period} | Tarih Aralığı: ${startStr} - ${endStr}`);
    console.log(`📊 Toplam kayıt: ${allData.length}`);
    // Önce filtrele
    globalModalData = allData.filter(record => {
        return compareDates(record.Tarih, startDate, endDate) && record.Sıra > 0;
    });
    // Sonra başlığı güncelle
    const modalTitle = document.getElementById('modalTitle');
    if (modalTitle) {
        modalTitle.textContent = `${startStr} - ${endStr} (${globalModalData.length} kayıt)`;
    }
    const globalModalTitle = document.getElementById('globalModalTitle');
    if (globalModalTitle) {
        globalModalTitle.textContent = `${startStr} - ${endStr} (${globalModalData.length} kayıt)`;
    }

    // Modal başlığı ve tabloyu güncelle
    const monthNames = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'];
    const currentMonthName = monthNames[today.getMonth()];
    const year = today.getFullYear();
    const labels = {
        'currentMonth': `Bu Ay (${currentMonthName} ${year})`,
        'currentYear': `Bu Yıl (01.01.${year} - 31.12.${year})`,
        'last3Years': `Son 3 Yıl (01.01.${year-2} - 31.12.${year})`,
        'since2020': `2020'den Beri (01.01.2020 - 31.12.${year})`
    };
    openGlobalStatsModal(globalModalData, labels[period]);
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
    // Farklı turnuva isimlerini bul (saat bilgisini ayrıştır)
    const uniqueTournaments = [];
    const tournamentSet = new Set();
    
    filtered.forEach(r => {
        const tournamentFull = r.Turnuva || '';
        // Turnuva adından saati çıkart: "TURNUVA ADI (26-12-2025 14:00)" -> "TURNUVA ADI", "26-12-2025 14:00"
        const timeMatch = tournamentFull.match(/(.+?)\s*\(([^)]+)\)\s*$/);
        const tournamentName = timeMatch ? timeMatch[1].trim() : tournamentFull;
        const tournamentTime = timeMatch ? timeMatch[2].trim() : '';
        
        const key = tournamentTime ? `${tournamentName}|${tournamentTime}` : tournamentName;
        
        if (!tournamentSet.has(key)) {
            tournamentSet.add(key);
            uniqueTournaments.push({
                displayName: tournamentFull,
                originalName: tournamentName,
                time: tournamentTime
            });
            console.log(`🎯 Turnuva eklendi: ${key}`);
        }
    });
    console.log(`✓ Toplam ${uniqueTournaments.length} adet turnuva bulundu`);
    
    if (uniqueTournaments.length > 1) {
        // Kullanıcıya seçim sun
        showTournamentSelectModal(uniqueTournaments, function(selectedTournament) {
            // selectedTournament = { displayName: ..., originalName: ..., time: ... }
            const tournamentData = filtered.filter(r => {
                const timeMatch = (r.Turnuva || '').match(/(.+?)\s*\(([^)]+)\)\s*$/);
                const name = timeMatch ? timeMatch[1].trim() : (r.Turnuva || '');
                const time = timeMatch ? timeMatch[2].trim() : '';
                
                // Seçilen turnuvayı eşleştir: originalName ve time ikisinin de eşleşmesi gerekir
                const isMatch = (name === selectedTournament.originalName && time === selectedTournament.time);
                console.log(`Filtering: "${name}|${time}" vs "${selectedTournament.originalName}|${selectedTournament.time}" = ${isMatch}`);
                return isMatch;
            });
            console.log(`✅ Seçilen turnuvadan ${tournamentData.length} kayıt bulundu`);
            openDailyResultsModal(tournamentData, filterDate);
        });
    } else if (uniqueTournaments.length === 1) {
        openDailyResultsModal(filtered, filterDate);
    } else {
        openDailyResultsModal(filtered, filterDate);
    }
}

// Turnuva seçimi modalı fonksiyonları
function showTournamentSelectModal(tournamentList, onSelect) {
    const modal = document.getElementById('tournamentSelectModal');
    const listDiv = document.getElementById('tournamentSelectList');
    listDiv.innerHTML = '';
    tournamentList.forEach(tournament => {
        const btn = document.createElement('button');
        // displayName veya originalName + time göster
        let displayText = tournament.displayName || '(isimsiz)';
        if (tournament.time) {
            // Time formatı: "26-12-2025 14:00" -> "14:00" olarak sadece saati göster
            const timeOnly = tournament.time.split(' ').pop(); // "14:00"
            displayText = `${tournament.originalName} - ${timeOnly}`;
        }
        btn.textContent = displayText;
        btn.style = 'display:block;width:100%;margin-bottom:12px;padding:12px;background:#ff9800;color:#fff;font-weight:bold;border:none;border-radius:8px;cursor:pointer;font-size:0.95em;text-align:center;';
        btn.onclick = () => {
            modal.style.display = 'none';
            if (onSelect) onSelect(tournament);
        };
        listDiv.appendChild(btn);
    });
    modal.style.display = 'block';
}

function closeTournamentSelectModal() {
    document.getElementById('tournamentSelectModal').style.display = 'none';
}

// Desktop masaüstü sonuçları göster
function showDesktopDailyResults(data, filterDate) {
    console.log('🖥️ Desktop sonuçları gösteriliyor - Veri:', data.length, 'Tarih:', filterDate);
    
    const grid = document.getElementById('directionResultsGrid');
    if (!grid) {
        console.error('❌ directionResultsGrid elementu bulunamadı!');
        return;
    }
    
    // Grid CSS'ini ayarla
    grid.style.display = 'block';
    grid.style.width = '100%';
    grid.style.padding = '20px';
    grid.style.boxSizing = 'border-box';
    grid.style.visibility = 'visible';
    grid.style.position = 'relative';
    grid.style.zIndex = '1';
    
    // Şampiyonları ve sıralamaları filtrele
    const nsChampions = data.filter(r => r.Direction === 'NS' && r['Sıra'] == 1);
    const ewChampions = data.filter(r => r.Direction === 'EW' && r['Sıra'] == 1);
    
    const nsRanked = data.filter(r => r.Direction === 'NS').sort((a, b) => {
        return parseInt(a['Sıra']) - parseInt(b['Sıra']);
    });
    
    const ewRanked = data.filter(r => r.Direction === 'EW').sort((a, b) => {
        return parseInt(a['Sıra']) - parseInt(b['Sıra']);
    });
    
    console.log('NS Şampiyonları:', nsChampions.length, 'EW Şampiyonları:', ewChampions.length);
    
    // Responsive ayarlar
    const isMobile = window.innerWidth < 700;
    const maxWidth = isMobile ? '100%' : '900px';
    const gridCols = isMobile ? '1fr' : '1fr 1fr';
    const fontSize = isMobile ? '0.75em' : '0.85em';
    const padding = isMobile ? '15px' : '20px';
    
    // Başlık
    let header = '<h2 style="color:#1e3c72;border-bottom:3px solid #667eea;padding-bottom:10px;margin-bottom:30px;text-align:center;font-size:' + (isMobile ? '1.3em' : '1.5em') + ';">📅 ' + filterDate + '</h2>';
    
    // SAYFA 1: Şampiyonlar (Ortada, responsive)
    let page1 = '<div style="display:flex;justify-content:center;margin-bottom:40px;"><div style="width:100%;max-width:' + maxWidth + ';"><div style="display:grid;grid-template-columns:' + gridCols + ';gap:' + padding + ';">';
    
    // NS Şampiyonları
    page1 += '<div style="background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);border-radius:12px;padding:20px;color:white;">';
    page1 += '<h3 style="margin:0 0 15px 0;text-align:center;font-size:1.1em;">🏆 Kuzey-Güney Şampiyonu</h3>';
    if (nsChampions.length > 0) {
        nsChampions.forEach(c => {
            page1 += '<div style="background:rgba(255,255,255,0.15);padding:12px;border-radius:8px;margin-bottom:8px;text-align:center;">';
            page1 += '<div style="font-size:1.3em;font-weight:bold;">' + c['Oyuncu 1'] + '</div>';
            page1 += '<div style="font-size:0.9em;opacity:0.9;">' + c['Oyuncu 2'] + '</div>';
            page1 += '<div style="font-size:0.8em;margin-top:5px;">% ' + c['Skor'] + '</div>';
            page1 += '</div>';
        });
    } else {
        page1 += '<div style="text-align:center;opacity:0.7;">Kayıt yok</div>';
    }
    page1 += '</div>';
    
    // EW Şampiyonları
    page1 += '<div style="background:linear-gradient(135deg, #f093fb 0%, #f5576c 100%);border-radius:12px;padding:20px;color:white;">';
    page1 += '<h3 style="margin:0 0 15px 0;text-align:center;font-size:1.1em;">🏆 Doğu-Batı Şampiyonu</h3>';
    if (ewChampions.length > 0) {
        ewChampions.forEach(c => {
            page1 += '<div style="background:rgba(255,255,255,0.15);padding:12px;border-radius:8px;margin-bottom:8px;text-align:center;">';
            page1 += '<div style="font-size:1.3em;font-weight:bold;">' + c['Oyuncu 1'] + '</div>';
            page1 += '<div style="font-size:0.9em;opacity:0.9;">' + c['Oyuncu 2'] + '</div>';
            page1 += '<div style="font-size:0.8em;margin-top:5px;">% ' + c['Skor'] + '</div>';
            page1 += '</div>';
        });
    } else {
        page1 += '<div style="text-align:center;opacity:0.7;">Kayıt yok</div>';
    }
    page1 += '</div></div></div></div>';
    
    // SAYFA 2-3: Sıralaması (responsive grid)
    let pageGridCols = isMobile ? '1fr' : '1fr 1fr';
    let page2 = '<div style="display:grid;grid-template-columns:' + pageGridCols + ';gap:' + padding + ';margin-bottom:30px;">';
    
    // NS Sıralaması
    page2 += '<div style="background:#f0f4ff;border-radius:12px;padding:' + padding + ';">';
    page2 += '<h3 style="margin:0 0 15px 0;text-align:center;color:#1e3c72;font-size:' + (isMobile ? '1em' : '1.1em') + ';">📊 Kuzey-Güney</h3>';
    page2 += '<table style="width:100%;border-collapse:collapse;font-size:' + fontSize + ';">';
    page2 += '<thead style="background:#667eea;color:white;"><tr><th style="padding:8px;text-align:center;border:none;">Sıra</th><th style="padding:8px;text-align:left;border:none;">Oyuncular</th><th style="padding:8px;text-align:center;border:none;">%</th></tr></thead><tbody>';
    nsRanked.forEach((r, idx) => {
        page2 += '<tr style="background:' + (idx % 2 === 0 ? 'white' : '#f9f9f9') + ';border-bottom:1px solid #e0e0e0;">';
        page2 += '<td style="padding:8px;text-align:center;font-weight:bold;color:#1e3c72;">' + r['Sıra'] + '</td>';
        page2 += '<td style="padding:8px;text-align:left;">' + r['Oyuncu 1'] + '<br/>' + r['Oyuncu 2'] + '</td>';
        page2 += '<td style="padding:8px;text-align:center;color:#667eea;font-weight:bold;">% ' + r['Skor'] + '</td>';
        page2 += '</tr>';
    });
    page2 += '</tbody></table></div>';
    
    // EW Sıralaması
    page2 += '<div style="background:#fff0f5;border-radius:12px;padding:' + padding + ';">';
    page2 += '<h3 style="margin:0 0 15px 0;text-align:center;color:#c2185b;font-size:' + (isMobile ? '1em' : '1.1em') + ';">📊 Doğu-Batı</h3>';
    page2 += '<table style="width:100%;border-collapse:collapse;font-size:' + fontSize + ';">';
    page2 += '<thead style="background:#f5576c;color:white;"><tr><th style="padding:8px;text-align:center;border:none;">Sıra</th><th style="padding:8px;text-align:left;border:none;">Oyuncular</th><th style="padding:8px;text-align:center;border:none;">%</th></tr></thead><tbody>';
    ewRanked.forEach((r, idx) => {
        page2 += '<tr style="background:' + (idx % 2 === 0 ? 'white' : '#f9f9f9') + ';border-bottom:1px solid #e0e0e0;">';
        page2 += '<td style="padding:8px;text-align:center;font-weight:bold;color:#c2185b;">' + r['Sıra'] + '</td>';
        page2 += '<td style="padding:8px;text-align:left;">' + r['Oyuncu 1'] + '<br/>' + r['Oyuncu 2'] + '</td>';
        page2 += '<td style="padding:8px;text-align:center;color:#f5576c;font-weight:bold;">% ' + r['Skor'] + '</td>';
        page2 += '</tr>';
    });
    page2 += '</tbody></table></div></div>';
    
    // Tüm içeriği birleştir
    const finalHTML = header + page1 + page2;
    
    grid.innerHTML = finalHTML;
    console.log('✅ Desktop sonuçları gösterildi - HTML uzunluğu:', finalHTML.length);
    
    try {
        alert('✅ Tarih seçimi sonuçları sayfanın aşağısında gösterildi!');
    } catch(e) {
        console.error('Alert hatası:', e);
    }
    
    // Scroll et
    setTimeout(() => {
        grid.scrollIntoView({ behavior: 'smooth', block: 'start' });
        console.log('✅ Scroll yapıldı');
    }, 100);
}

// ===== DAILY RESULTS MODAL (3 PAGES) =====
function openDailyResultsModal(data, filterDate) {
    console.log('📱 openDailyResultsModal çağrıldı - Genişlik:', window.innerWidth, 'Veri:', data.length);
    
    if (!databaseReady) {
        document.getElementById('fileInfo').innerHTML = '<span style="color:orange;">⚠️ Veritabanı yüklenmeden modal açılamaz.</span>';
        return;
    }

    if (window.innerWidth < 700) {
        console.log('❌ MOBIL MODU (genişlik < 700)');
        const mobileModal = document.getElementById('mobileResultsModal');
        console.log('mobileResultsModal element:', mobileModal);
        if (mobileModal) {
            mobileModal.style.display = 'block';
            document.body.style.overflow = 'hidden';

            // Store data globally for tab switching
            window.dailyModalData = data;
            window.currentDailyTab = 1;
            
            // Show tab 1 by default
            showDailyResultTab(1);
        }
    } else {
        console.log('✅ MASAÜSTÜ MODU (genişlik >= 700) - showDesktopDailyResults çağrılıyor');
        // Desktop version - Show results in sections below
        showDesktopDailyResults(data, filterDate);
    }
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
    
    // Update page indicator
    if (currentPageEl) currentPageEl.textContent = tabNum;
    
    // Butonların görünürlüğünü kontrol et
    if (prevBtn) prevBtn.style.visibility = tabNum > 1 ? 'visible' : 'hidden';
    if (nextBtn) nextBtn.style.visibility = tabNum < 3 ? 'visible' : 'hidden';
    
    if (tabNum === 1) {
        // Tab 1: Şampiyonlar
        if (header) header.textContent = '👑 Günün Şampiyonları';
        
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
        html += `<div style='color:#1ca7c1;font-weight:bold;font-size:0.9em;text-align:center;'>🗻 Kuzey-Güney</div>`;
        if (nsChamps.length === 0) {
            html += `<div style='color:#999;text-align:center;'>Veri yok</div>`;
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
        html += `<div style='color:#6db66d;font-weight:bold;font-size:0.9em;text-align:center;'>↔️ Doğu-Batı</div>`;
        if (ewChamps.length === 0) {
            html += `<div style='color:#999;text-align:center;'>Veri yok</div>`;
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
        
        contentArea.innerHTML = html;
        
    } else if (tabNum === 2) {
        // Tab 2: Kuzey-Güney Sonuçları
        if (header) header.textContent = '🗻 Kuzey-Güney Sonuçları';
        
        const nsResults = data.filter(row => row['Direction'] === 'NS').sort((a, b) => {
            const aRank = parseInt(a['Sıra']) || 999;
            const bRank = parseInt(b['Sıra']) || 999;
            return aRank - bRank;
        });
        
        let html = '';
        if (nsResults.length === 0) {
            html += `<div style='text-align:center;color:#999;'>Sonuç bulunamadı</div>`;
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
        contentArea.innerHTML = html;
        
    } else if (tabNum === 3) {
        // Tab 3: Doğu-Batı Sonuçları
        if (header) header.textContent = '↔️ Doğu-Batı Sonuçları';
        
        const ewResults = data.filter(row => row['Direction'] === 'EW').sort((a, b) => {
            const aRank = parseInt(a['Sıra']) || 999;
            const bRank = parseInt(b['Sıra']) || 999;
            return aRank - bRank;
        });
        
        let html = '';
        if (ewResults.length === 0) {
            html += `<div style='text-align:center;color:#999;'>Sonuç bulunamadı</div>`;
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
        contentArea.innerHTML = html;
    }
}

function updateDailyNav(page) {
    const totalSpan = document.getElementById('totalPages');
    if (totalSpan) totalSpan.textContent = '3';

    const currentPageSpan = document.getElementById('currentPage');
    if (currentPageSpan) currentPageSpan.textContent = page;

    // Get buttons correctly - they are direct children of resultsNavigation
    const resultsNav = document.getElementById('resultsNavigation');
    if (resultsNav) {
        const buttons = resultsNav.querySelectorAll('button');
        if (buttons.length >= 2) {
            const prevBtn = buttons[0];
            const nextBtn = buttons[1];
            if (prevBtn) prevBtn.style.visibility = page > 1 ? 'visible' : 'hidden';
            if (nextBtn) nextBtn.style.visibility = page < 3 ? 'visible' : 'hidden';
        }
    }

    const headerLabel = document.getElementById('modalHeaderLabel');
    if (headerLabel) {
        if (page === 1) headerLabel.textContent = '👑 Günün Şampiyonları';
        else if (page === 2) headerLabel.textContent = '🗻 Kuzey-Güney Sonuçları';
        else if (page === 3) headerLabel.textContent = '↔️ Doğu-Batı Sonuçları';
    }
}

function goToNextPageDaily() {
    const pagesContainer = document.getElementById('pagesContainer');
    const currentPageEl = document.getElementById('currentPage');
    
    if (!pagesContainer || !currentPageEl) {
        console.log('❌ pagesContainer veya currentPageEl bulunamadı');
        return;
    }
    
    let page = parseInt(currentPageEl.textContent, 10) || 1;
    console.log('📄 Şu sayfada: ' + page + ', Sonraki sayfaya git');
    
    if (page < 3) {
        page++;
        const translatePercent = ((page - 1) / 3) * 100;
        console.log('🔄 Transform: translateX(-' + translatePercent + '%)');
        pagesContainer.style.transform = `translateX(-${translatePercent}%)`;
        updateDailyNav(page);
    }
}

function goToPreviousPageDaily() {
    const pagesContainer = document.getElementById('pagesContainer');
    const currentPageEl = document.getElementById('currentPage');
    
    if (!pagesContainer || !currentPageEl) {
        console.log('❌ pagesContainer veya currentPageEl bulunamadı');
        return;
    }
    
    let page = parseInt(currentPageEl.textContent, 10) || 1;
    console.log('📄 Şu sayfada: ' + page + ', Önceki sayfaya git');
    
    if (page > 1) {
        page--;
        const translatePercent = ((page - 1) / 3) * 100;
        console.log('🔄 Transform: translateX(-' + translatePercent + '%)');
        pagesContainer.style.transform = `translateX(-${translatePercent}%)`;
        updateDailyNav(page);
    }
}

// ===== MODAL OPENING =====
function openGlobalStatsModal(data, filterLabel) {
    if (!databaseReady) {
        // Database not ready, queue this modal open
        queuedModalOpen = [data, filterLabel];
        document.getElementById('fileInfo').innerHTML = '<span style="color:orange;">⚠️ Veritabanı yüklenmeden modal açılamaz.</span>';
        return;
    }
    globalModalData = data;
    // Set modal header label for both mobile and desktop
    const headerLabel = document.getElementById('modalHeaderLabel');
    if (headerLabel) {
        let labelText = 'Sonuçlar';
        // Detect language (default: Turkish)
        let lang = 'tr';
        if (navigator.language && navigator.language.startsWith('en')) lang = 'en';
        if (filterLabel) {
            if (filterLabel.includes('Bu Ay')) {
                labelText = lang === 'en' ? "This Month's Results" : 'Bu Ayın Sonuçları';
            } else if (filterLabel.includes('Bu Yıl')) {
                labelText = lang === 'en' ? "This Year's Results" : 'Bu Yılın Sonuçları';
            } else if (filterLabel.includes('Son 3 Yıl')) {
                labelText = lang === 'en' ? "Last 3 Year's Results" : 'Son 3 Yılın Sonuçları';
            } else if (filterLabel.includes("2020'den Beri")) {
                labelText = lang === 'en' ? "Results Since 2020" : "2020'den itibaren Sonuçlar";
            }
        }
        headerLabel.textContent = labelText;
    }
    // Detect mobile (width < 700px)
    if (window.innerWidth < 700) {
        // Show mobile modal
        const mobileModal = document.getElementById('mobileResultsModal');
        if (mobileModal) {
            mobileModal.style.display = 'block';
            document.body.style.overflow = 'hidden';
            
            // Page 1: İstatistikler (Bireysel Oyuncu)
            const statsContent = document.getElementById('statsContent');
            if (statsContent) {
                // Container'ı flex layout yapıp sayfayı tamamen kapla
                statsContent.style.display = 'flex';
                statsContent.style.flexDirection = 'column';
                statsContent.style.height = '100%';
                statsContent.style.overflow = 'hidden';
                
                let html = ``;
                
                // Bireysel oyuncu istatistikleri
                const playerStats = {};
                data.forEach(row => {
                    const p1 = row['Oyuncu 1'];
                    const p2 = row['Oyuncu 2'];
                    const score = parseFloat(row['Skor']);
                    const isFirst = row['Sıra'] === '1' || row['Sıra'] === 1;
                    
                    // Oyuncu 1
                    if (!playerStats[p1]) {
                        playerStats[p1] = { firstPlaceCount: 0, totalScore: 0, count: 0 };
                    }
                    if (isFirst) playerStats[p1].firstPlaceCount++;
                    if (!isNaN(score)) {
                        playerStats[p1].totalScore += score;
                        playerStats[p1].count++;
                    }
                    
                    // Oyuncu 2
                    if (!playerStats[p2]) {
                        playerStats[p2] = { firstPlaceCount: 0, totalScore: 0, count: 0 };
                    }
                    if (isFirst) playerStats[p2].firstPlaceCount++;
                    if (!isNaN(score)) {
                        playerStats[p2].totalScore += score;
                        playerStats[p2].count++;
                    }
                });
                
                // En Çok 1'incilik Alanlar
                const topFirst = Object.entries(playerStats)
                    .map(([name, stats]) => ({
                        name,
                        count: stats.firstPlaceCount
                    }))
                    .filter(x => x.count > 0)
                    .sort((a, b) => b.count - a.count)
                    .slice(0, 3);
                
                html += `<div style='flex:1;display:flex;flex-direction:column;margin-bottom:10px;'>`;
                html += `<div style='background:linear-gradient(90deg, #ff9800 0%, #fb8c00 50%, #ff9800 100%);border-radius:10px 10px 0 0;padding:16px;border-top:4px solid #e65100;box-shadow:0 2px 8px rgba(255, 152, 0, 0.3);'>`;
                html += `<div style='font-weight:bold;color:white;font-size:1.25em;text-shadow:1px 1px 2px rgba(0,0,0,0.2);'>🏆 En Çok 1'incilik Alanlar</div>`;
                html += `</div>`;
                html += `<div style='background:#fff3e0;border-radius:0 0 12px 12px;padding:10px 12px;border:1px solid #ffe0b2;border-top:none;flex:1;overflow:hidden;'>`;
                if (topFirst.length === 0) {
                    html += `<div style='color:#888;font-size:0.9em;'>Veri yok</div>`;
                } else {
                    topFirst.forEach((item, idx) => {
                        html += `<div style='font-size:0.85em;margin-bottom:5px;padding-bottom:5px;border-bottom:1px solid #ffe0b2;'>`;
                        html += `<div style='font-weight:bold;color:#1e3c72;margin-bottom:2px;line-height:1.2;'>${idx + 1}. ${item.name}</div>`;
                        html += `<div style='color:#ff9800;font-weight:bold;font-size:0.85em;'>${item.count} kez Birinci</div>`;
                        html += `</div>`;
                    });
                }
                html += `</div>`;
                html += `</div>`;
                
                // En Yüksek Ortalama Skorlar
                const topScores = Object.entries(playerStats)
                    .map(([name, stats]) => ({
                        name,
                        avg: stats.count > 0 ? (stats.totalScore / stats.count).toFixed(2) : 0,
                        count: stats.count
                    }))
                    .filter(x => x.count > 0)
                    .sort((a, b) => parseFloat(b.avg) - parseFloat(a.avg))
                    .slice(0, 3);
                
                html += `<div style='flex:1;display:flex;flex-direction:column;'>`;
                html += `<div style='background:linear-gradient(90deg, #2196f3 0%, #1976d2 50%, #2196f3 100%);border-radius:10px 10px 0 0;padding:16px;border-top:4px solid #0d47a1;box-shadow:0 2px 8px rgba(33, 150, 243, 0.3);'>`;
                html += `<div style='font-weight:bold;color:white;font-size:1.25em;text-shadow:1px 1px 2px rgba(0,0,0,0.2);'>📈 En Yüksek Ortalama Skorlar</div>`;
                html += `</div>`;
                html += `<div style='background:#e3f2fd;border-radius:0 0 12px 12px;padding:10px 12px;border:1px solid #bbdefb;border-top:none;flex:1;overflow:hidden;'>`;
                if (topScores.length === 0) {
                    html += `<div style='color:#888;font-size:0.9em;'>Veri yok</div>`;
                } else {
                    topScores.forEach((item, idx) => {
                        html += `<div style='font-size:0.85em;margin-bottom:5px;padding-bottom:5px;border-bottom:1px solid #bbdefb;'>`;
                        html += `<div style='font-weight:bold;color:#1e3c72;margin-bottom:2px;line-height:1.2;'>${idx + 1}. ${item.name}</div>`;
                        html += `<div style='color:#2196f3;font-weight:bold;font-size:0.8em;'>% ${item.avg} <span style='color:#999;'>(${item.count} maç)</span></div>`;
                        html += `</div>`;
                    });
                }
                html += `</div>`;
                html += `</div>`;
                
                statsContent.innerHTML = html;
            }
            
            // Page 2: Turnuva Sonuçları (Tarihsel Dönemlere Göre)
            const resultsContent = document.getElementById('resultsContent');
            if (resultsContent) {
                // Verileri tarihe göre grupla
                const resultsByDate = {};
                const allResults = [
                    ...data.filter(row => row['Direction'] === 'NS').map(r => ({...r, type: 'NS'})),
                    ...data.filter(row => row['Direction'] === 'EW').map(r => ({...r, type: 'EW'}))
                ];
                
                allResults.forEach(row => {
                    const date = row['Tarih'] || 'Belirtilmemiş';
                    if (!resultsByDate[date]) {
                        resultsByDate[date] = [];
                    }
                    resultsByDate[date].push(row);
                });
                
                // Tarihleri sırala (eski → yeni)
                const sortedDates = Object.keys(resultsByDate).sort((a, b) => {
                    if (a === 'Belirtilmemiş') return 1;
                    if (b === 'Belirtilmemiş') return -1;
                    return new Date(a) - new Date(b);
                });
                
                // Gün adını almak için yardımcı fonksiyon
                function getDayName(dateStr) {
                    const days = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar'];
                    try {
                        const date = new Date(dateStr);
                        return days[date.getDay()];
                    } catch {
                        return '';
                    }
                }
                
                let html = ``;
                
                // Excel export butonu
                const totalRecords = allResults.length;
                html += `<div style='background:linear-gradient(135deg, #90EE90 0%, #6BB66D 100%);border-radius:12px;padding:12px 14px;margin-bottom:16px;display:flex;align-items:center;justify-content:space-between;color:white;box-shadow:0 4px 6px rgba(107, 182, 109, 0.3);'>`;
                html += `<div style='font-weight:bold;font-size:0.95em;'>📁 Excel Dosyası</div>`;
                html += `<button id='exportToExcelBtn' style='background:white;color:#6BB66D;border:none;padding:6px 14px;border-radius:6px;font-weight:bold;cursor:pointer;font-size:0.9em;'>İndir</button>`;
                html += `</div>`;
                
                if (allResults.length === 0) {
                    html += `<div style='color:#888;text-align:center;'>Sonuç bulunamadı.</div>`;
                } else {
                    sortedDates.forEach(date => {
                        const dateResults = resultsByDate[date];
                        const dayName = getDayName(date);
                        
                        // Tarih dönem başlığı
                        html += `<div style='background:linear-gradient(90deg, #667eea 0%, #764ba2 100%);border-radius:8px;padding:12px 14px;margin-bottom:12px;box-shadow:0 2px 6px rgba(102, 126, 234, 0.25);'>`;
                        html += `<div style='font-weight:bold;color:white;font-size:1em;'>📅 ${date} ${dayName ? `<span style='margin-left:12px;'>${dayName}</span>` : ''}</div>`;
                        html += `</div>`;
                        
                        // Tarih dönemine ait sonuçlar
                        dateResults.forEach(row => {
                            const bgColor = row.type === 'NS' ? '#eaf6fb' : '#f0faea';
                            const dirColor = row.type === 'NS' ? '#20B2AA' : '#6db66d';
                            const dirLabel = row.type === 'NS' ? 'NS' : 'EW';
                            html += `<div style='background:${bgColor};border-radius:8px;padding:12px 14px;margin-bottom:10px;box-shadow:0 1px 4px rgba(30,60,114,0.06);display:flex;align-items:center;gap:10px;'>`;
                            html += `<div style='font-weight:bold;color:#1e3c72;min-width:50px;text-align:center;'>${dirLabel}-${row['Sıra']}</div>`;
                            html += `<div style='color:#ccc;'>|</div>`;
                            html += `<div style='font-weight:bold;color:#1e3c72;flex:1;line-height:1.3;word-wrap:break-word;overflow-wrap:break-word;'>${row['Oyuncu 1']} - ${row['Oyuncu 2']}</div>`;
                            html += `<div style='color:${dirColor};font-weight:bold;white-space:nowrap;'>% ${row['Skor']}</div>`;
                            html += `</div>`;
                        });
                        
                        html += `<div style='height:8px;'></div>`;
                    });
                }
                
                resultsContent.innerHTML = html;
                
                // Excel export butonu işlevselliği
                const exportBtn = resultsContent.querySelector('#exportToExcelBtn');
                if (exportBtn) {
                    exportBtn.addEventListener('click', () => {
                        exportResultsToExcel(allResults);
                    });
                }
            }
            
            // Reset to page 1
            const pagesContainer = document.getElementById('pagesContainer');
            if (pagesContainer) {
                pagesContainer.style.transform = 'translateX(0)';
            }
            updateMobileNav(1);
        }
    } else {
        // Desktop modal
        const modal = document.getElementById('globalStatsModal');
        if (modal) {
            modal.style.display = 'block';
            modal.style.visibility = 'visible';
            modal.style.opacity = '1';
            modal.style.zIndex = '99999';
            document.body.style.overflow = 'hidden';
        }
        // Always start at page 1 and render it
        currentGlobalPage = 1;
        if (typeof renderGlobalPage1 === 'function') {
            renderGlobalPage1();
        } else {
            // fallback: render champions if function missing
            content = document.getElementById('globalModalContent');
            if (content) {
                content.innerHTML = `<h2 style=\"text-align:center;color:#1e3c72;margin:16px 0 20px 0;font-size:1.2em;\">👑 Günün Şampiyonları</h2><div id=\"statsGrid\"></div>`;
                displayChampions(globalModalData);
            }
        }
    }
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
        let mainUrl = '/database.json?v=' + Date.now();
        let fallbackUrl = '/database_temp.json?v=' + Date.now();
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
                                    const today = new Date().toLocaleDateString('tr-TR');
                                    document.getElementById('fileInfo').innerHTML = `<span style='color:green;'>✓ Veri Güncelleme ${today} & ${allData.length} kayıt</span>`;
                                    databaseReady = true;
                                    // Oyuncu aramasını initialize et
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
                    const today = new Date().toLocaleDateString('tr-TR');
                    document.getElementById('fileInfo').innerHTML = `<span style='color:green;'>✓ Veri Güncelleme ${today} & ${allData.length} kayıt</span>`;
                    databaseReady = true;
                    // Oyuncu aramasını initialize et
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

// ===== GLOBAL RANGE MODAL (2 PAGES) =====
function openGlobalRangeModal(data, period) {
    window.rangeModalData = data;
    window.currentRangeTab = 1;
    
    const modal = document.getElementById('globalRangeModal');
    if (modal) {
        modal.style.display = 'block';
        showGlobalRangeTab(1);
    }
}

function closeGlobalRangeModal() {
    const modal = document.getElementById('globalRangeModal');
    if (modal) modal.style.display = 'none';
}

function showGlobalRangeTab(tabNum) {
    if (tabNum < 1) tabNum = 1;
    if (tabNum > 2) tabNum = 2;
    
    window.currentRangeTab = tabNum;
    
    const data = window.rangeModalData || [];
    const content = document.getElementById('rangeModalContent');
    const title = document.getElementById('rangeModalTitle');
    const pageIndicator = document.getElementById('rangePageIndicator');
    const prevBtn = document.getElementById('rangePrevBtn');
    const nextBtn = document.getElementById('rangeNextBtn');
    
    if (pageIndicator) pageIndicator.textContent = `Sayfa ${tabNum}/2`;
    if (prevBtn) prevBtn.style.visibility = tabNum > 1 ? 'visible' : 'hidden';
    if (nextBtn) nextBtn.style.visibility = tabNum < 2 ? 'visible' : 'hidden';
    
    if (tabNum === 1) {
        if (title) title.textContent = '📊 Turnuva İstatistikleri';
        // İstatistikler sayfası
        
        // 1. En fazla 1.lik alanlar
        const firstPlaces = {};
        data.filter(r => r['Sıra'] === 1 || r['Sıra'] === '1').forEach(r => {
            firstPlaces[r['Oyuncu 1']] = (firstPlaces[r['Oyuncu 1']] || 0) + 1;
            firstPlaces[r['Oyuncu 2']] = (firstPlaces[r['Oyuncu 2']] || 0) + 1;
        });
        
        const topFirst = Object.entries(firstPlaces)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 3);
        
        // 2. En yüksek ortalama skor
        const playerScores = {};
        data.forEach(r => {
            const score = parseFloat(r['Skor']) || 0;
            if (!playerScores[r['Oyuncu 1']]) playerScores[r['Oyuncu 1']] = { sum: 0, count: 0 };
            if (!playerScores[r['Oyuncu 2']]) playerScores[r['Oyuncu 2']] = { sum: 0, count: 0 };
            playerScores[r['Oyuncu 1']].sum += score;
            playerScores[r['Oyuncu 1']].count += 1;
            playerScores[r['Oyuncu 2']].sum += score;
            playerScores[r['Oyuncu 2']].count += 1;
        });
        
        const topAverage = Object.entries(playerScores)
            .map(([name, stats]) => [name, stats.sum / stats.count])
            .sort((a, b) => b[1] - a[1])
            .slice(0, 3);
        
        let html = `<div style='padding:20px 10px;'>
            <!-- 1.lik Sayısı Container -->
            <div style='margin-bottom:30px;'>
                <h3 style='color:#1e3c72;margin-bottom:15px;font-size:1.1em;'>🏆 En Fazla 1.lik Alanlar</h3>
                <div style='background:#eaf6fb;border:2px solid #1ca7c1;border-radius:8px;padding:20px;'>`;
        
        topFirst.forEach((item, idx) => {
            const [name, count] = item;
            const medal = idx === 0 ? '🥇' : idx === 1 ? '🥈' : '🥉';
            html += `<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:${idx === topFirst.length - 1 ? '0' : '15px'};'>
                <div style='display:flex;align-items:center;gap:10px;'>
                    <span style='font-size:1.5em;'>${medal}</span>
                    <span style='font-weight:bold;color:#1e3c72;'>${name}</span>
                </div>
                <span style='background:#1ca7c1;color:white;padding:8px 16px;border-radius:6px;font-weight:bold;min-width:100px;text-align:center;'>${count} kez</span>
            </div>`;
        });
        
        html += `</div></div>
            
            <!-- Ortalama Skor Container -->
            <div>
                <h3 style='color:#1e3c72;margin-bottom:15px;font-size:1.1em;'>⭐ En Yüksek Ortalama Skor</h3>
                <div style='background:#f0faea;border:2px solid #6db66d;border-radius:8px;padding:20px;'>`;
        
        topAverage.forEach((item, idx) => {
            const [name, average] = item;
            const medal = idx === 0 ? '🥇' : idx === 1 ? '🥈' : '🥉';
            html += `<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:${idx === topAverage.length - 1 ? '0' : '15px'};'>
                <div style='display:flex;align-items:center;gap:10px;'>
                    <span style='font-size:1.5em;'>${medal}</span>
                    <span style='font-weight:bold;color:#1e3c72;'>${name}</span>
                </div>
                <span style='background:#6db66d;color:white;padding:8px 16px;border-radius:6px;font-weight:bold;min-width:100px;text-align:center;'>% ${average.toFixed(2)}</span>
            </div>`;
        });
        
        html += `</div></div></div>`;
        
        content.innerHTML = html;
    } else if (tabNum === 2) {
        if (title) title.textContent = '🏆 Turnuva Sonuçları';
        // Sonuçlar sayfası - Tarih bazında gruplandırılmış
        let html = `<div style='padding:20px;'>
            <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;'>
                <h3 style='color:#1e3c72;margin:0;font-size:1.2em;'>🏆 Sonuçlar</h3>
                <button onclick='exportRangeResultsToExcel()' style='padding:10px 15px;background:#ff9800;color:white;border:none;border-radius:6px;cursor:pointer;font-weight:bold;font-size:0.9em;'>📥 Excel'e Aktar</button>
            </div>
            <div style='max-height:450px;overflow-y:auto;border:1px solid #ddd;border-radius:6px;'>`;
        
        // Tarihine göre sırala ve grupla (en eski ilk)
        const sorted = [...data].sort((a, b) => {
            const dateA = a['Tarih'].split('.').reverse().join('');
            const dateB = b['Tarih'].split('.').reverse().join('');
            return dateA.localeCompare(dateB);
        });
        
        const gunAdları = ['Pazar', 'Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi'];
        let currentDate = null;
        
        sorted.forEach((row, idx) => {
            // Tarih değişmişse yeni başlık yap
            if (currentDate !== row['Tarih']) {
                currentDate = row['Tarih'];
                const [day, month, year] = currentDate.split('.');
                const date = new Date(year, month - 1, day);
                const gunAdi = gunAdları[date.getDay()];
                
                html += `<div style='background:#1e3c72;color:white;padding:12px 15px;font-weight:bold;font-size:1em;margin-top:10px;'>
                    ${day}.${month}.${year} - ${gunAdi}
                </div>`;
            }
            
            // Sıra ve Yön birleştir
            const dir = row['Direction'] === 'NS' ? 'NS' : 'EW';
            const sıra = `${row['Sıra']} ${dir}`;
            
            // Sonuç kartı
            html += `<div style='padding:12px 15px;border-bottom:1px solid #eee;display:flex;gap:15px;align-items:flex-start;'>
                <div style='flex:0 0 45px;font-weight:bold;background:${dir === 'NS' ? '#eaf6fb' : '#f0faea'};color:${dir === 'NS' ? '#1ca7c1' : '#6db66d'};padding:6px 10px;border-radius:4px;text-align:center;font-size:0.9em;'>${sıra}</div>
                <div style='flex:1;'>
                    <div style='font-weight:bold;color:#1e3c72;margin-bottom:4px;font-size:0.95em;'>${row['Oyuncu 1']}</div>
                    <div style='font-weight:bold;color:#1e3c72;margin-bottom:4px;font-size:0.95em;'>${row['Oyuncu 2']}</div>
                </div>
                <div style='flex:0 0 auto;font-weight:bold;color:#1e3c72;text-align:center;'>
                    <div style='font-size:1.3em;'>${row['Skor']}</div>
                </div>
            </div>`;
        });
        
        html += `</div></div>`;
        content.innerHTML = html;
    }
}

function exportRangeResultsToExcel() {
    const data = window.rangeModalData || [];
    if (data.length === 0) {
        alert('Dışa aktarılacak veri yok!');
        return;
    }
    
    const exportData = data.map(row => ({
        'Tarih': row['Tarih'],
        'Oyuncu 1': row['Oyuncu 1'],
        'Oyuncu 2': row['Oyuncu 2'],
        'Yön': row['Direction'] === 'NS' ? 'Kuzey-Güney' : 'Doğu-Batı',
        'Sıra': row['Sıra'],
        '% Skor': row['Skor']
    }));
    
    const worksheet = XLSX.utils.json_to_sheet(exportData);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Sonuçlar');
    
    worksheet['!cols'] = [
        { wch: 12 },
        { wch: 18 },
        { wch: 18 },
        { wch: 12 },
        { wch: 8 },
        { wch: 10 }
    ];
    
    const fileName = `Turnuva_Sonuclari_${new Date().toLocaleDateString('tr-TR').replace(/\./g, '_')}.xlsx`;
    XLSX.writeFile(workbook, fileName);
}

console.log('✓ script.js yüklendi - Tüm fonksiyonlar hazır');
