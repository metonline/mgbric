<?php
echo "=== 02.01.2026 TEST ===\n\n";

// auto_update_vugraph.py'yi 02.01.2026 için çalıştır
$cmd = "/usr/bin/python3 /home/mgb3dcinfo/public_html/hosgoru/auto_update_vugraph.py 2>&1";
$output = shell_exec($cmd);

// Output'u ara
if (strpos($output, '02.01.2026') !== false) {
    echo "02.01.2026 kontrol edildi:\n";
    // 02.01.2026 satırlarını göster
    $lines = explode("\n", $output);
    $show = false;
    foreach ($lines as $line) {
        if (strpos($line, '02.01.2026') !== false) {
            $show = true;
        }
        if ($show) {
            echo $line . "\n";
            if (strpos($line, '02.01.2026') !== false && strpos($line, 'çekiliyor') === false) {
                break;
            }
        }
    }
} else {
    echo "02.01.2026 kontrol edilmedi!\n";
}

echo "\n=== FULL OUTPUT ===\n";
echo $output;
?>
