// ===== QUICK DATE FILTER BUTTON HANDLER =====
function setDateRangeFilter(period, event) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    window.period = period;
    loadDatabase();
}
// ===== MOBILE MODAL PAGE NAVIGATION =====
function goToNextPage() {
    const pagesContainer = document.getElementById('pagesContainer');
    const currentPage = document.getElementById('currentPage');
    if (!pagesContainer || !currentPage) return;
    let page = parseInt(currentPage.textContent, 10);
        if (page < 2) {
        page++;
        pagesContainer.style.left = `-${(page-1)*100}%`;
        currentPage.textContent = page;
    }
        // Hide 'Sonraki' button if on last page
        const nextBtn = document.querySelector('#resultsNavigation button:last-child');
        if (nextBtn) {
            if (parseInt(currentPage.textContent, 10) === 2) {
                nextBtn.style.display = 'none';
            } else {
                nextBtn.style.display = '';
            }
        }
}

function goToPreviousPage() {
    const pagesContainer = document.getElementById('pagesContainer');
    const currentPage = document.getElementById('currentPage');
    if (!pagesContainer || !currentPage) return;
    let page = parseInt(currentPage.textContent, 10);
    if (page > 1) {
        page--;
        pagesContainer.style.left = `-${(page-1)*100}%`;
        currentPage.textContent = page;
    }
        // Show 'Sonraki' button if not on last page
        const nextBtn = document.querySelector('#resultsNavigation button:last-child');
        if (nextBtn) {
            if (parseInt(currentPage.textContent, 10) < 2) {
                nextBtn.style.display = '';
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
        console.warn('⚠️ Veritabanı henüz hazır değil. Bekleniyor...');
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
    console.log(`📋 İlk 3 kayıt:`, allData.slice(0, 3));
    const filtered = allData.filter(record => {
        const recordDate = record.Tarih;
        return recordDate === filterDate;
    });
    console.log(`✅ Filtrelenen kayıt: ${filtered.length}`);
    console.log(`🔎 Arama kriterleri - filterDate: "${filterDate}"`);
    if (filtered.length === 0) {
        // Veritabanındaki benzersiz tarihleri göster (ilk 10)
        const uniqueDates = [...new Set(allData.map(r => r.Tarih))];
        console.warn(`⚠️ Tarih eşleşmedi. Veritabanındaki tarihler:`, uniqueDates.slice(0, 10));
        alert(`${filterDate} tarihinde kayıt bulunamadı.\n\nVeritabanındaki tarihler:\n${uniqueDates.slice(0, 5).join('\n')}`);
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
            console.log('Mobile modal data sample:', data ? data.slice(0, 2) : 'NO DATA');
                // Page 1: Günün Şampiyonları
                const championsContent = document.getElementById('championsContent');
                if (championsContent) {
                    // Calculate stats
                    let firsts = {};
                    data.forEach(row => {
                        if (row['Sıra'] == 1) {
                            const key = row['Oyuncu 1'];
                            if (!firsts[key]) firsts[key] = { count: 0, scores: [] };
                            firsts[key].count++;
                            firsts[key].scores.push(Number(row['Skor']));
                        }
                    });
                    let firstsArr = Object.entries(firsts).map(([name, obj]) => ({ name, count: obj.count, avg: (obj.scores.reduce((a,b)=>a+b,0)/obj.scores.length).toFixed(2) }));
                    firstsArr.sort((a,b) => b.count - a.count || b.avg - a.avg);
                    // Modern kart tasarımı
                    let html = `<div style='background:#e3f0ff;border-radius:12px;padding:18px 12px 12px 12px;margin-bottom:18px;border:2px solid #a3bffa;box-shadow:0 2px 8px rgba(30,60,114,0.08);'>`;
                    html += `<div style='font-size:1.3em;font-weight:bold;color:#1e3c72;margin-bottom:8px;display:flex;align-items:center;gap:8px;'><span style='font-size:1.2em;'>�</span> Günün Şampiyonları</div>`;
                    if (firstsArr.length === 0) {
                        html += `<div style='color:#888;text-align:center;'>Şampiyon bulunamadı.</div>`;
                    } else {
                        firstsArr.forEach((x,i) => {
                            html += `<div style='background:#fff;border-radius:8px;padding:12px;margin-bottom:10px;box-shadow:0 1px 4px rgba(30,60,114,0.06);display:flex;align-items:center;gap:12px;'>`;
                            html += `<div style='font-size:1.2em;font-weight:bold;color:#3b5998;width:32px;text-align:center;'>${i+1}</div>`;
                            html += `<div style='flex:1;'><div style='font-weight:bold;color:#1e3c72;'>${x.name}</div><div style='color:#888;font-size:0.95em;'>${x.count} kez - Ort: ${x.avg}</div></div>`;
                            html += `</div>`;
                        });
                    }
                    html += `</div>`;
                    championsContent.innerHTML = html;
                }
                // Page 2: Kuzey-Güney Sonuçları (NS)
                const nsResultsContent = document.getElementById('nsResultsContent');
                if (nsResultsContent) {
                    const filtered = data.filter(row => row['Direction'] === 'NS');
                    let html = `<div style='font-size:1.2em;font-weight:bold;color:#1ca7c1;margin-bottom:10px;text-align:center;'>Kuzey-Güney Sonuçları</div>`;
                    if (filtered.length === 0) {
                        html += `<div style='color:#888;text-align:center;'>Sonuç bulunamadı.</div>`;
                    } else {
                        filtered.forEach(row => {
                            html += `<div style='background:#eaf6fb;border-radius:8px;padding:12px 16px;margin-bottom:12px;box-shadow:0 1px 4px rgba(30,60,114,0.06);'>`;
                            html += `<div style='font-weight:bold;color:#1e3c72;'>[${row['Sıra']}] ${row['Oyuncu 1']} - ${row['Oyuncu 2']}</div>`;
                            html += `<div style='color:#1ca7c1;font-weight:bold;'>${row['Skor']}</div>`;
                            html += `</div>`;
                        });
                    }
                    nsResultsContent.innerHTML = html;
                }
                // Page 3: Doğu-Batı Sonuçları (EW)
                const ewResultsContent = document.getElementById('ewResultsContent');
                if (ewResultsContent) {
                    const filtered = data.filter(row => row['Direction'] === 'EW');
                    let html = `<div style='font-size:1.2em;font-weight:bold;color:#6db66d;margin-bottom:10px;text-align:center;'>Doğu-Batı Sonuçları</div>`;
                    if (filtered.length === 0) {
                        html += `<div style='color:#888;text-align:center;'>Sonuç bulunamadı.</div>`;
                    } else {
                        filtered.forEach(row => {
                            html += `<div style='background:#f0faea;border-radius:8px;padding:12px 16px;margin-bottom:12px;box-shadow:0 1px 4px rgba(30,60,114,0.06);'>`;
                            html += `<div style='font-weight:bold;color:#1e3c72;'>[${row['Sıra']}] ${row['Oyuncu 1']} - ${row['Oyuncu 2']}</div>`;
                            html += `<div style='color:#6db66d;font-weight:bold;'>${row['Skor']}</div>`;
                            html += `</div>`;
                        });
                    }
                    ewResultsContent.innerHTML = html;
                }
                // Set to first page and update page count to 3
                const pagesContainer = document.getElementById('pagesContainer');
                if (pagesContainer) pagesContainer.style.left = '0%';
                const currentPage = document.getElementById('currentPage');
                if (currentPage) currentPage.textContent = '1';
                const totalPages = document.getElementById('totalPages');
                if (totalPages) totalPages.textContent = '3';
                // Always show/hide 'Sonraki' button correctly on open
                const nextBtn = document.querySelector('#resultsNavigation button:last-child');
                if (nextBtn) nextBtn.style.display = '';
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
                                    document.getElementById('fileInfo').innerHTML = `<span style='color:green;'>✓ Yedek veritabanı yüklendi (${allData.length} kayıt)</span>`;
                                    databaseReady = true;
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
                    document.getElementById('fileInfo').innerHTML = `<span style='color:green;'>✓ Veritabanı yüklendi (${allData.length} kayıt)</span>`;
                    databaseReady = true;
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

// ===== MOBİL MODAL FONKSİYONLARI =====

function showMobileModal(data) {
    if (!data || data.length === 0) return;
    
    currentModalPage = 1;
    
    // Desktop bölümlerini gizle
    const statsSection = document.getElementById('statsSection');
    const directionSection = document.getElementById('directionResultsSection');
    const championsSection = document.getElementById('championsSection');
    
    if (statsSection) statsSection.style.display = 'none';
    if (directionSection) directionSection.style.display = 'none';
    if (championsSection) championsSection.style.display = 'none';
    
    // Sayfaları doldur
    fillMobilePages(data);
    
    // Modal'ı aç
    const modal = document.getElementById('mobileResultsModal');
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }
    
    updatePageDisplay();
}

function fillMobilePages(data) {
    if (!data || data.length === 0) return;
    
    // Sayfa 1: Şampiyonlar (her yönün 1.si)
    const championsContent = document.getElementById('championsContent');
    if (championsContent) {
        const nsChampion = data
            .filter(row => row['Direction'] === 'NS')
            .sort((a, b) => parseInt(a['Sıra']) - parseInt(b['Sıra']))[0];
        const ewChampion = data
            .filter(row => row['Direction'] === 'EW')
            .sort((a, b) => parseInt(a['Sıra']) - parseInt(b['Sıra']))[0];

        let html = `<div style='background:#e8f2ff;border-radius:12px;padding:16px;border:2px solid #b6c9ff;box-shadow:0 2px 8px rgba(30,60,114,0.08);'>`;
        html += `<div style='font-size:1.2em;font-weight:bold;color:#1e3c72;margin-bottom:14px;text-align:center;'><span style='font-size:1.1em;'>👑</span> Günün Şampiyonları</div>`;

        // Flexbox wrap: responsive, eşit boyut, tüm alanı kapla
        html += `<div style='display:flex;flex-wrap:wrap;gap:10px;'>`;

        // Kuzey-Güney 1.si
        html += `<div style='flex:1 1 calc(50% - 5px);min-width:180px;background:#f0f8ff;border-radius:8px;padding:14px;box-shadow:0 1px 3px rgba(30,60,114,0.06);display:flex;flex-direction:column;justify-content:space-between;'>`;
        html += `<div style='color:#20B2AA;font-weight:bold;margin-bottom:8px;font-size:0.95em;'>Kuzey-Güney 1.si</div>`;
        if (nsChampion) {
            html += `<div style='font-weight:bold;color:#1e3c72;line-height:1.4;word-wrap:break-word;overflow-wrap:break-word;flex-grow:1;display:flex;align-items:center;'>${nsChampion['Oyuncu 1']} - ${nsChampion['Oyuncu 2']}</div>`;
            html += `<div style='color:#20B2AA;font-weight:bold;margin-top:8px;font-size:1.1em;'>% ${nsChampion['Skor']}</div>`;
        } else {
            html += `<div style='color:#888;text-align:center;'>Veri yok</div>`;
        }
        html += `</div>`;

        // Doğu-Batı 1.si
        html += `<div style='flex:1 1 calc(50% - 5px);min-width:180px;background:#f2fbe9;border-radius:8px;padding:14px;box-shadow:0 1px 3px rgba(30,60,114,0.06);display:flex;flex-direction:column;justify-content:space-between;'>`;
        html += `<div style='color:#6DB66D;font-weight:bold;margin-bottom:8px;font-size:0.95em;'>Doğu-Batı 1.si</div>`;
        if (ewChampion) {
            html += `<div style='font-weight:bold;color:#1e3c72;line-height:1.4;word-wrap:break-word;overflow-wrap:break-word;flex-grow:1;display:flex;align-items:center;'>${ewChampion['Oyuncu 1']} - ${ewChampion['Oyuncu 2']}</div>`;
            html += `<div style='color:#6DB66D;font-weight:bold;margin-top:8px;font-size:1.1em;'>% ${ewChampion['Skor']}</div>`;
        } else {
            html += `<div style='color:#888;text-align:center;'>Veri yok</div>`;
        }
        html += `</div>`;

        html += `</div>`; // flex wrap end
        html += `</div>`;
        championsContent.innerHTML = html;
    }
    
    // Sayfa 2: Kuzey-Güney Sonuçları (NS)
    const nsResultsContent = document.getElementById('nsResultsContent');
    if (nsResultsContent) {
        const filtered = data.filter(row => row['Direction'] === 'NS')
            .sort((a, b) => parseInt(a['Sıra']) - parseInt(b['Sıra']));
        let html = `<div style='font-size:1.2em;font-weight:bold;color:#1ca7c1;margin-bottom:10px;text-align:center;'>Kuzey-Güney Sonuçları</div>`;
        if (filtered.length === 0) {
            html += `<div style='color:#888;text-align:center;'>Sonuç bulunamadı.</div>`;
        } else {
            filtered.forEach(row => {
                html += `<div style='background:#eaf6fb;border-radius:8px;padding:12px 16px;margin-bottom:12px;box-shadow:0 1px 4px rgba(30,60,114,0.06); word-break: break-word; line-height:1.25;'>`;
                html += `<div style='font-weight:bold;color:#1e3c72;'>[${row['Sıra']}] ${row['Oyuncu 1']} - ${row['Oyuncu 2']}</div>`;
                html += `<div style='color:#666;font-size:0.9em;margin-top:4px;'>Ort: ${row['Skor']}</div>`;
                html += `</div>`;
            });
        }
        nsResultsContent.innerHTML = html;
    }
    
    // Sayfa 3: Doğu-Batı Sonuçları (EW)
    const ewResultsContent = document.getElementById('ewResultsContent');
    if (ewResultsContent) {
        const filtered = data.filter(row => row['Direction'] === 'EW')
            .sort((a, b) => parseInt(a['Sıra']) - parseInt(b['Sıra']));
        let html = `<div style='font-size:1.2em;font-weight:bold;color:#6DB66D;margin-bottom:10px;text-align:center;'>Doğu-Batı Sonuçları</div>`;
        if (filtered.length === 0) {
            html += `<div style='color:#888;text-align:center;'>Sonuç bulunamadı.</div>`;
        } else {
            filtered.forEach(row => {
                html += `<div style='background:#f3f8ef;border-radius:8px;padding:12px 16px;margin-bottom:12px;box-shadow:0 1px 4px rgba(30,60,114,0.06); word-break: break-word; line-height:1.25;'>`;
                html += `<div style='font-weight:bold;color:#1e3c72;'>[${row['Sıra']}] ${row['Oyuncu 1']} - ${row['Oyuncu 2']}</div>`;
                html += `<div style='color:#666;font-size:0.9em;margin-top:4px;'>Ort: ${row['Skor']}</div>`;
                html += `</div>`;
            });
        }
        ewResultsContent.innerHTML = html;
    }
}

function goToPage(pageNum) {
    if (pageNum >= 1 && pageNum <= 3) {
        currentModalPage = pageNum;
        updatePageDisplay();
    }
}

function goToPreviousPage() {
    if (currentModalPage > 1) {
        goToPage(currentModalPage - 1);
    } else {
        closeMobileModal();
    }
}

function goToNextPage() {
    if (currentModalPage < 3) {
        goToPage(currentModalPage + 1);
    }
}

function updatePageDisplay() {
    const container = document.getElementById('pagesContainer');
    if (container) {
        const offset = (currentModalPage - 1) * -100;
        container.style.transform = `translateX(${offset}%)`;
    }
    
    const indicator = document.getElementById('currentPage');
    if (indicator) {
        indicator.textContent = currentModalPage;
    }
    
    const prevBtn = document.querySelector('#resultsNavigation button:first-child');
    const nextBtn = document.querySelector('#resultsNavigation button:last-child');
    
    if (prevBtn && nextBtn) {
        if (currentModalPage === 3) {
            prevBtn.style.visibility = 'visible';
            nextBtn.style.visibility = 'hidden';
        } else if (currentModalPage === 1) {
            prevBtn.style.visibility = 'hidden';
            nextBtn.style.visibility = 'visible';
        } else {
            prevBtn.style.visibility = 'visible';
            nextBtn.style.visibility = 'visible';
        }
    }
}

function closeMobileModal() {
    const modal = document.getElementById('mobileResultsModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
    
    document.getElementById('championsContent').innerHTML = '';
    document.getElementById('nsResultsContent').innerHTML = '';
    document.getElementById('ewResultsContent').innerHTML = '';
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

console.log('✓ script.js yüklendi - Tüm fonksiyonlar hazır');
