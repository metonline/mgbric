<?php
echo "=== CRON TEST ===\n\n";

// Test 1: Python yolu
echo "1. Python kontrol:\n";
$python_test = shell_exec('/usr/bin/python3 --version 2>&1');
echo $python_test . "\n";

// Test 2: Script varlığı
echo "\n2. Script dosyası kontrol:\n";
$script_path = '/home/mgb3dcinfo/public_html/hosgoru/auto_update_vugraph.py';
if (file_exists($script_path)) {
    echo "✓ Script var: $script_path\n";
} else {
    echo "✗ Script YOK: $script_path\n";
}

// Test 3: Auto-update çalıştır
echo "\n3. Auto-update çalıştırılıyor...\n";
$output = shell_exec('/usr/bin/python3 ' . escapeshellarg($script_path) . ' 2>&1');
echo $output;

echo "\n=== TEST BITTI ===\n";
?>
