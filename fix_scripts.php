<?php
// Sunucuda Python script'lerini düzelt
$dir = "/home/mgb3dcinfo/public_html/hosgoru/";

// 1. auto_update_vugraph.py düzelt
$file1 = $dir . "auto_update_vugraph.py";
$content1 = file_get_contents($file1);

// Eski satırı yeni satırla değiştir
$old1 = "sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))";
$new1 = "SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))\nsys.path.insert(0, SCRIPT_DIR)\nDB_FILE = os.path.join(SCRIPT_DIR, 'database.json')";

if (strpos($content1, "DB_FILE") === false) {
    $content1 = str_replace($old1, $new1, $content1);
    $content1 = str_replace("with open('database.json',", "with open(DB_FILE,", $content1);
    file_put_contents($file1, $content1);
    echo "✅ auto_update_vugraph.py güncellendi<br>";
} else {
    echo "ℹ️ auto_update_vugraph.py zaten güncellenmiş<br>";
}

// 2. vugraph_fetcher.py düzelt
$file2 = $dir . "vugraph_fetcher.py";
$content2 = file_get_contents($file2);

if (strpos($content2, "import os") === false || strpos($content2, "DB_FILE") === false) {
    $content2 = str_replace(
        "import sys",
        "import sys\nimport os",
        $content2
    );
    
    $content2 = str_replace(
        "BASE_URL = \"https://clubs.vugraph.com/hosgoru\"",
        "BASE_URL = \"https://clubs.vugraph.com/hosgoru\"\n    DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.json')",
        $content2
    );
    
    $content2 = str_replace("with open('database.json',", "with open(self.DB_FILE,", $content2);
    
    file_put_contents($file2, $content2);
    echo "✅ vugraph_fetcher.py güncellendi<br>";
} else {
    echo "ℹ️ vugraph_fetcher.py zaten güncellenmiş<br>";
}

echo "<hr>";
echo "Sonraki adım: Cron job'ı manuel olarak çalıştır";
?>
