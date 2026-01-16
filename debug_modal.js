// Browser console'da çalıştırılacak debug script
// Tarayıcıda F12 → Console sekmesine kopyala/yapıştır

console.log('=== GlobalRangeModal Debug Test ===');

// 1. Database kontrolü
console.log('1. Database kontrol:');
console.log('  allData:', allData ? allData.length + ' records' : 'NOT LOADED');
console.log('  databaseReady:', databaseReady);

// 2. Modal element kontrolü
console.log('2. Modal elements:');
console.log('  globalRangeModal:', document.getElementById('globalRangeModal') ? 'FOUND' : 'NOT FOUND');
console.log('  rangeModalContent:', document.getElementById('rangeModalContent') ? 'FOUND' : 'NOT FOUND');
console.log('  rangeModalTitle:', document.getElementById('rangeModalTitle') ? 'FOUND' : 'NOT FOUND');

// 3. Filtre butonları kontrolü
console.log('3. Filter buttons:');
const buttons = document.querySelectorAll('[onclick*="setDateRangeFilter"]');
console.log('  Found', buttons.length, 'filter buttons');
buttons.forEach(btn => {
    console.log('  -', btn.textContent.trim(), btn.onclick);
});

// 4. "Bu Ay" filtresini manuel çalıştır
console.log('4. Running "Bu Ay" filter manually...');
if (databaseReady && allData) {
    // Simulate setDateRangeFilter('currentMonth')
    window.period = 'currentMonth';
    
    // Get current month boundaries
    const today = new Date();
    const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
    const lastDay = today;
    
    const parseDate = (dateStr) => {
        if (!dateStr) return null;
        const [day, month, year] = dateStr.split('.');
        return new Date(year, month - 1, day);
    };
    
    const filtered = allData.filter(record => {
        if (!record.Tarih || record.Sıra <= 0) return false;
        const recordDate = parseDate(record.Tarih);
        if (!recordDate) return false;
        return recordDate >= firstDay && recordDate <= lastDay;
    });
    
    console.log('  Filtered:', filtered.length, 'records for currentMonth');
    
    // Assign to global variable (simulating loadDatabase)
    window.globalModalData = filtered;
    window.globalRangeData = filtered;
    
    console.log('  window.globalModalData:', window.globalModalData.length);
    console.log('  window.globalRangeData:', window.globalRangeData.length);
    
    // Test openGlobalRangeModal
    console.log('5. Calling openGlobalRangeModal...');
    try {
        openGlobalRangeModal(filtered, '📅 Bu Ay (Manual Test)');
        console.log('  ✓ Modal açıldı!');
        
        // Check if showGlobalRangeTab ran
        console.log('  window.currentRangeTab:', window.currentRangeTab);
        console.log('  Modal display:', document.getElementById('globalRangeModal').style.display);
        
    } catch (error) {
        console.error('  ✗ Error:', error.message);
        console.error('  Stack:', error.stack);
    }
} else {
    console.log('  ERROR: Database not ready!');
}
