<?php
echo "=== EVENT 404197 TEST ===\n\n";

// Event 404197'yi doğrudan çekmeye çalış
$event_url = "https://clubs.vugraph.com/hosgoru/eventresults.php?event=404197";
$context = stream_context_create([
    'http' => ['timeout' => 10]
]);

echo "Fetching: $event_url\n\n";
$html = @file_get_contents($event_url, false, $context);

if ($html) {
    echo "✓ Sayfa alındı (" . strlen($html) . " bytes)\n";
    
    // Sonuç sayısını bul
    if (preg_match('/Found (\d+) results/i', $html, $m)) {
        echo "✓ Sonuç bulundu: " . $m[1] . "\n";
    }
    
    // Board sayısını bul
    if (preg_match('/Board (\d+)/i', $html, $m)) {
        echo "✓ Board sayısı: " . $m[1] . "\n";
    }
    
    // NS/EW tabloları bul
    if (preg_match_all('/<table[^>]*>.*?<\/table>/si', $html, $tables)) {
        echo "✓ Tablo sayısı: " . count($tables[0]) . "\n";
    }
} else {
    echo "✗ Sayfa alınamadı!\n";
}

echo "\n=== TEST BITTI ===\n";
?>
