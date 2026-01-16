<?php
echo "=== PIP INSTALL TEST ===\n\n";

// Gerekli paketleri yükle
$packages = ['beautifulsoup4', 'requests', 'lxml'];

foreach ($packages as $pkg) {
    echo "Installing: $pkg\n";
    $cmd = "/usr/bin/python3 -m pip install $pkg 2>&1";
    $output = shell_exec($cmd);
    echo $output . "\n";
}

echo "\n=== INSTALLATION DONE ===\n";
?>
