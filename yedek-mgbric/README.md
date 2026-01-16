# Hoşgörü Turnuva Analiz ve Tarayıcı (TR/EN)

## TR
- Amaç: Kulüp takviminden turnuva sonuçlarını çekmek ve web arayüzünde analiz etmek.
- Akış:
  - `run_bot.py` ile sonuçları tarayın, `database.xlsx` güncellenir.
  - `index.html` + `script.js` ile Excel verisini yükleyip filtreleyin ve istatistiklere bakın.
- Hızlı Başlangıç:
  1. Python ortamında bağımlılıkları kurun:
     ```bash
     pip install pandas requests beautifulsoup4 openpyxl
     ```
  2. Botu çalıştırın (Türkçe çıktı, 3 deneme):
     ```bash
     python run_bot.py --lang tr --retries 3
     ```
  3. Excel dosyası çalışma dizininde `database.xlsx` olarak oluşur/güncellenir.
  4. Tarayıcıda `index.html` dosyasını açın.

- Dil (CLI):
  - `--lang tr|en` ile terminal çıktısını Türkçe/İngilizce seçebilirsiniz.
  - Bot, ortam değişkeni `HOSGORU_LANG` üzerinden dili alır.

## EN
- Purpose: Fetch tournament results from the club calendar and analyze them in the web UI.
- Flow:
  - Run `run_bot.py` to scrape results; it updates `database.xlsx`.
  - Use `index.html` + `script.js` to load Excel data, filter, and view stats.
- Quick Start:
  1. Install dependencies in your Python environment:
     ```bash
     pip install pandas requests beautifulsoup4 openpyxl
     ```
  2. Run the bot (English output, 3 retries):
     ```bash
     python run_bot.py --lang en --retries 3
     ```
  3. Excel file `database.xlsx` is created/updated in the working directory.
  4. Open `index.html` in your browser.

- Language (CLI):
  - Select terminal output language via `--lang tr|en`.
  - The scraper reads language from the `HOSGORU_LANG` environment variable.

## Notes
- Web UI supports TR/EN via an in-page language selector.
- Stats include global summaries and per-player insights.
- If site structure changes, scraping may need adjustments.
