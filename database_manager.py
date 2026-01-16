#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Veritabanı Yönetim Sistemi
Database Management System for Bridge Tournament Data
"""

from flask import Flask, render_template_string, request, jsonify
import json
import os
from datetime import datetime
import shutil
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import threading

app = Flask(__name__)

DATABASE_FILE = 'database.json'
BACKUP_DIR = 'backups'
TEMP_FILE = 'database_temp.json'

# Backup klasörünü oluştur
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

class VugraphScraper:
    BASE_URL = "https://clubs.vugraph.com/hosgoru"
    CALENDAR_URL = f"{BASE_URL}/calendar.php"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_calendar(self):
        """Takvim sayfasını indir"""
        try:
            response = self.session.get(self.CALENDAR_URL, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')
            
            links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href and 'results.php' in href:
                    full_url = urljoin(self.BASE_URL, href)
                    text = link.get_text(strip=True)
                    links.append({'url': full_url, 'text': text})
            
            return links
        except:
            return []
    
    def fetch_results(self, url):
        """Turnuva sonuçlarını indir"""
        try:
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')
            
            records = []
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:
                    cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
                    if len(cells) >= 5:
                        record = self.parse_record(cells)
                        if record:
                            records.append(record)
            
            return records
        except:
            return []
    
    def parse_record(self, cells):
        """Satırı kayda dönüştür"""
        try:
            if len(cells) >= 5:
                record = {
                    'Tarih': cells[1],
                    'Oyuncu 1': cells[2].upper(),
                    'Oyuncu 2': cells[3].upper(),
                    'Skor': int(cells[4]) if cells[4].isdigit() else 0,
                    'Direction': 'NS',
                    'Turnuva': 'Hosgoru'
                }
                
                if len(cells) >= 6:
                    direction = cells[5].strip().upper().replace('/', '')
                    if direction in ['NS', 'EW']:
                        record['Direction'] = direction
                
                if 'Tarih' in record and 'Oyuncu 1' in record:
                    return record
        except:
            pass
        
        return None
    
    def scrape_all(self, progress_callback=None):
        """Tüm turnuvaları scrape et"""
        all_records = []
        links = self.fetch_calendar()
        
        for i, link in enumerate(links, 1):
            if progress_callback:
                progress_callback(f"Processing {i}/{len(links)}: {link['text']}")
            
            records = self.fetch_results(link['url'])
            all_records.extend(records)
        
        return all_records

def load_database():
    """Veritabanını yükle"""
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_database(data):
    """Veritabanını kaydet"""
    with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=0)

def create_backup():
    """Yedek oluştur"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(BACKUP_DIR, f'database_backup_{timestamp}.json')
    shutil.copy(DATABASE_FILE, backup_file)
    return backup_file

def get_next_sira(data):
    """Sonraki Sıra numarasını bul"""
    if not data:
        return 1
    return max(r.get('Sıra', 0) for r in data) + 1

def get_statistics():
    """Veritabanı istatistiklerini al"""
    data = load_database()
    
    # Tarih aralığını hesapla
    dates = [r.get('Tarih', '') for r in data if r.get('Tarih')]
    
    # Turnuva türlerini say
    tournaments = {}
    for record in data:
        tournament = record.get('Turnuva', 'Bilinmiyor')
        tournaments[tournament] = tournaments.get(tournament, 0) + 1
    
    return {
        'total_records': len(data),
        'min_date': min(dates) if dates else 'N/A',
        'max_date': max(dates) if dates else 'N/A',
        'tournaments': tournaments,
        'max_sira': max(r.get('Sıra', 0) for r in data) if data else 0
    }

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Veritabanı Yönetim Sistemi</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            padding: 40px;
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            text-align: center;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-value { font-size: 28px; font-weight: bold; }
        .stat-label { font-size: 12px; opacity: 0.9; margin-top: 5px; }
        
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #eee;
        }
        .tab-button {
            background: none;
            border: none;
            padding: 15px 20px;
            cursor: pointer;
            font-size: 16px;
            color: #666;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }
        .tab-button.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #333;
            font-weight: 500;
        }
        input, textarea, select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
            font-family: inherit;
        }
        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .btn-group {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }
        button {
            padding: 12px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4); }
        .btn-secondary {
            background: #f0f0f0;
            color: #333;
        }
        .btn-secondary:hover { background: #e0e0e0; }
        .btn-danger {
            background: #ff6b6b;
            color: white;
        }
        .btn-danger:hover { background: #ee5a5a; }
        
        .alert {
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .alert-info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        
        .tournament-list {
            list-style: none;
            background: #f9f9f9;
            padding: 15px;
            border-radius: 5px;
        }
        .tournament-list li {
            padding: 8px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
        }
        .tournament-list li:last-child {
            border-bottom: none;
        }
        
        .file-input-wrapper {
            position: relative;
            display: inline-block;
            width: 100%;
        }
        .file-input-wrapper input[type="file"] {
            display: none;
        }
        .file-label {
            display: block;
            padding: 10px;
            background: #f0f0f0;
            border: 2px dashed #667eea;
            border-radius: 5px;
            cursor: pointer;
            text-align: center;
            transition: all 0.3s;
        }
        .file-label:hover {
            background: #e8e8e8;
        }
        
        .record-form {
            background: #f9f9f9;
            padding: 20px;
            border-radius: 5px;
        }
        
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏆 Veritabanı Yönetim Sistemi</h1>
        <p class="subtitle">Bridge Turnuvası Veri Yönetim Paneli</p>
        
        <!-- İstatistikler -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="stat-total">0</div>
                <div class="stat-label">Toplam Kayıt</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="stat-min-date">-</div>
                <div class="stat-label">En Eski Tarih</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="stat-max-date">-</div>
                <div class="stat-label">En Yeni Tarih</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="stat-tournaments">0</div>
                <div class="stat-label">Turnuva Türü</div>
            </div>
        </div>
        
        <!-- Sekmeler -->
        <div class="tabs">
            <button class="tab-button active" onclick="switchTab('add-record')">➕ Yeni Kayıt Ekle</button>
            <button class="tab-button" onclick="switchTab('bulk-add')">📊 Toplu Ekle (Excel)</button>
            <button class="tab-button" onclick="switchTab('vugraph')">🌐 Vugraph Scraper</button>
            <button class="tab-button" onclick="switchTab('backup')">💾 Yedek & Geri Yükle</button>
            <button class="tab-button" onclick="switchTab('tournaments')">🎯 Turnuvaları Görüntüle</button>
        </div>
        
        <!-- Yeni Kayıt Ekle -->
        <div id="add-record" class="tab-content active">
            <div class="record-form">
                <h2 style="margin-bottom: 20px;">Yeni Kayıt Ekle</h2>
                <div class="form-group">
                    <label>Tarih (DD.MM.YYYY)</label>
                    <input type="text" id="new-date" placeholder="01.12.2025" required>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Oyuncu 1</label>
                        <input type="text" id="new-player1" placeholder="OYUNCU ADI" required>
                    </div>
                    <div class="form-group">
                        <label>Oyuncu 2</label>
                        <input type="text" id="new-player2" placeholder="OYUNCU ADI" required>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Skor</label>
                        <input type="number" id="new-score" placeholder="500" required>
                    </div>
                    <div class="form-group">
                        <label>Direction (NS/EW)</label>
                        <input type="text" id="new-direction" placeholder="NS" required>
                    </div>
                </div>
                <div class="form-group">
                    <label>Turnuva</label>
                    <input type="text" id="new-tournament" placeholder="Turnuva Adı" required>
                </div>
                <div class="btn-group" style="grid-template-columns: 1fr;">
                    <button class="btn-primary" onclick="addSingleRecord()">Kayıt Ekle</button>
                </div>
                <div id="message-add-record"></div>
            </div>
        </div>
        
        <!-- Toplu Ekle -->
        <div id="bulk-add" class="tab-content">
            <h2 style="margin-bottom: 20px;">Excel Dosyasından Toplu Ekle</h2>
            <div class="alert alert-info">
                📝 Excel dosyası şu sütunları içermeli: Tarih, Oyuncu 1, Oyuncu 2, Skor, Direction, Turnuva
            </div>
            <div class="form-group">
                <label>Excel Dosyası Seç</label>
                <div class="file-input-wrapper">
                    <input type="file" id="excel-file" accept=".xlsx,.xls" onchange="handleFileUpload(event)">
                    <label for="excel-file" class="file-label">
                        📁 Dosyayı seçmek için tıklayın veya sürükleyin
                    </label>
                </div>
            </div>
            <div class="btn-group" style="grid-template-columns: 1fr;">
                <button class="btn-primary" onclick="uploadExcel()">Yükle ve Ekle</button>
            </div>
            <div id="message-bulk-add"></div>
        </div>
        
        <!-- Vugraph Scraper -->
        <div id="vugraph" class="tab-content">
            <h2 style="margin-bottom: 20px;">Vugraph Hoşgörü Briç Sitesinden İndir</h2>
            <div class="alert alert-info">
                🌐 <strong>https://clubs.vugraph.com/hosgoru/</strong> sitesinden tüm turnuva verilerini otomatik indir
            </div>
            <div class="btn-group" style="grid-template-columns: 1fr;">
                <button class="btn-primary" onclick="startVugraphScrape()">🚀 Scraping Başlat</button>
            </div>
            <div id="vugraph-progress" style="margin-top: 20px;"></div>
            <div id="message-vugraph"></div>
        </div>
        
        <!-- Yedek & Geri Yükle -->
        <div id="backup" class="tab-content">
            <h2 style="margin-bottom: 20px;">Yedek & Geri Yükle</h2>
            <div class="btn-group">
                <button class="btn-primary" onclick="createBackup()">💾 Şimdi Yedek Oluştur</button>
                <button class="btn-secondary" onclick="listBackups()">📋 Yedekleri Listele</button>
            </div>
            <div id="backup-list" style="margin-top: 20px;"></div>
            <div id="message-backup"></div>
        </div>
        
        <!-- Turnuvaları Görüntüle -->
        <div id="tournaments" class="tab-content">
            <h2 style="margin-bottom: 20px;">Turnuva Türleri ve Kayıt Sayıları</h2>
            <ul class="tournament-list" id="tournament-list">
                <li>Yükleniyor...</li>
            </ul>
            <div id="message-tournaments"></div>
        </div>
    </div>
    
    <script>
        function switchTab(tabName) {
            // Tüm sekmeleri gizle
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-button').forEach(el => el.classList.remove('active'));
            
            // Seçilen sekmeyi göster
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            
            // İstatistikleri güncelle
            updateStatistics();
        }
        
        function updateStatistics() {
            fetch('/api/statistics')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('stat-total').textContent = data.total_records.toLocaleString();
                    document.getElementById('stat-min-date').textContent = data.min_date;
                    document.getElementById('stat-max-date').textContent = data.max_date;
                    document.getElementById('stat-tournaments').textContent = Object.keys(data.tournaments).length;
                });
        }
        
        function addSingleRecord() {
            const record = {
                Tarih: document.getElementById('new-date').value,
                'Oyuncu 1': document.getElementById('new-player1').value,
                'Oyuncu 2': document.getElementById('new-player2').value,
                Skor: parseInt(document.getElementById('new-score').value),
                Direction: document.getElementById('new-direction').value.toUpperCase(),
                Turnuva: document.getElementById('new-tournament').value
            };
            
            if (!record.Tarih || !record['Oyuncu 1'] || !record['Oyuncu 2'] || !record.Skor || !record.Direction || !record.Turnuva) {
                showMessage('message-add-record', 'Lütfen tüm alanları doldurun!', 'error');
                return;
            }
            
            fetch('/api/add-record', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(record)
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    showMessage('message-add-record', `✅ Kayıt başarıyla eklendi! (Sıra: ${data.sira})`, 'success');
                    // Formu temizle
                    document.getElementById('new-date').value = '';
                    document.getElementById('new-player1').value = '';
                    document.getElementById('new-player2').value = '';
                    document.getElementById('new-score').value = '';
                    document.getElementById('new-direction').value = '';
                    document.getElementById('new-tournament').value = '';
                    updateStatistics();
                } else {
                    showMessage('message-add-record', `❌ Hata: ${data.error}`, 'error');
                }
            });
        }
        
        function handleFileUpload(event) {
            const file = event.target.files[0];
            if (file) {
                document.querySelector('.file-label').textContent = `📄 ${file.name}`;
            }
        }
        
        function uploadExcel() {
            const fileInput = document.getElementById('excel-file');
            if (!fileInput.files.length) {
                showMessage('message-bulk-add', 'Lütfen bir dosya seçin!', 'error');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            
            fetch('/api/upload-excel', {
                method: 'POST',
                body: formData
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    showMessage('message-bulk-add', `✅ ${data.added} kayıt başarıyla eklendi!`, 'success');
                    updateStatistics();
                } else {
                    showMessage('message-bulk-add', `❌ Hata: ${data.error}`, 'error');
                }
            });
        }
        
        function startVugraphScrape() {
            const btn = event.target;
            btn.disabled = true;
            btn.textContent = '⏳ Scraping başladı...';
            
            const progressDiv = document.getElementById('vugraph-progress');
            progressDiv.innerHTML = '<div class="alert alert-info">📡 Vugraph sitesinden veriler indiriliyor. Lütfen bekleyin...</div>';
            
            fetch('/api/scrape-vugraph', {
                method: 'POST'
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    showMessage('message-vugraph', 
                        `✅ ${data.added} yeni kayıt eklendi! (Toplam: ${data.total})`, 'success');
                    progressDiv.innerHTML = '';
                    updateStatistics();
                } else {
                    showMessage('message-vugraph', `❌ Hata: ${data.error}`, 'error');
                }
                
                btn.disabled = false;
                btn.textContent = '🚀 Scraping Başlat';
            })
            .catch(err => {
                showMessage('message-vugraph', `❌ Bağlantı hatası: ${err}`, 'error');
                btn.disabled = false;
                btn.textContent = '🚀 Scraping Başlat';
            });
        }
        
        function createBackup() {
            fetch('/api/backup', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        showMessage('message-backup', `✅ Yedek başarıyla oluşturuldu!`, 'success');
                        listBackups();
                    } else {
                        showMessage('message-backup', `❌ Hata: ${data.error}`, 'error');
                    }
                });
        }
        
        function listBackups() {
            fetch('/api/backups')
                .then(r => r.json())
                .then(data => {
                    const html = '<h3 style="margin-bottom: 15px;">Mevcut Yedekler</h3><ul class="tournament-list">' +
                        data.backups.map(b => 
                            `<li><span>${b}</span><button class="btn-danger" onclick="restoreBackup('${b}')" style="width:auto;padding:5px 10px;">Geri Yükle</button></li>`
                        ).join('') +
                        '</ul>';
                    document.getElementById('backup-list').innerHTML = html;
                });
        }
        
        function restoreBackup(filename) {
            if (!confirm(`${filename} dosyasından geri yüklemek istediğinize emin misiniz?`)) return;
            
            fetch('/api/restore-backup', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({filename})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    showMessage('message-backup', `✅ Yedek başarıyla geri yüklendi!`, 'success');
                    updateStatistics();
                } else {
                    showMessage('message-backup', `❌ Hata: ${data.error}`, 'error');
                }
            });
        }
        
        function showMessage(elementId, message, type) {
            const element = document.getElementById(elementId);
            element.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
        }
        
        // Sayfa yüklendiğinde istatistikleri güncelle
        document.addEventListener('DOMContentLoaded', updateStatistics);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/statistics')
def api_statistics():
    stats = get_statistics()
    return jsonify(stats)

@app.route('/api/add-record', methods=['POST'])
def api_add_record():
    try:
        data = load_database()
        record = request.json
        record['Sıra'] = get_next_sira(data)
        data.append(record)
        save_database(data)
        
        return jsonify({
            'success': True,
            'sira': record['Sıra'],
            'message': f"Kayıt başarıyla eklendi (Sıra: {record['Sıra']})"
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/backup', methods=['POST'])
def api_backup():
    try:
        backup_file = create_backup()
        return jsonify({
            'success': True,
            'message': f'Yedek oluşturuldu: {backup_file}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/backups')
def api_backups():
    try:
        backups = sorted(os.listdir(BACKUP_DIR), reverse=True)
        return jsonify({'backups': backups})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/restore-backup', methods=['POST'])
def api_restore_backup():
    try:
        filename = request.json['filename']
        backup_path = os.path.join(BACKUP_DIR, filename)
        
        if not os.path.exists(backup_path):
            return jsonify({'success': False, 'error': 'Yedek dosyası bulunamadı'})
        
        shutil.copy(backup_path, DATABASE_FILE)
        return jsonify({'success': True, 'message': 'Yedek geri yüklendi'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/upload-excel', methods=['POST'])
def api_upload_excel():
    try:
        import openpyxl
        
        file = request.files['file']
        wb = openpyxl.load_workbook(file)
        ws = wb.active
        
        data = load_database()
        added_count = 0
        
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row and any(row):
                try:
                    record = {
                        'Sıra': get_next_sira(data),
                        'Tarih': str(row[0]) if row[0] else '',
                        'Oyuncu 1': str(row[1]) if row[1] else '',
                        'Oyuncu 2': str(row[2]) if row[2] else '',
                        'Skor': int(row[3]) if row[3] else 0,
                        'Direction': str(row[4]).upper() if row[4] else '',
                        'Turnuva': str(row[5]) if row[5] else ''
                    }
                    
                    if record['Tarih'] and record['Oyuncu 1']:
                        data.append(record)
                        added_count += 1
                except:
                    continue
        
        save_database(data)
        return jsonify({
            'success': True,
            'added': added_count,
            'message': f'{added_count} kayıt eklendi'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/scrape-vugraph', methods=['POST'])
def api_scrape_vugraph():
    try:
        scraper = VugraphScraper()
        new_records = scraper.scrape_all()
        
        data = load_database()
        before_count = len(data)
        
        # Duplicate kontrol et (Tarih + Oyuncu1 + Oyuncu2 kombinasyonuna göre)
        existing_keys = set()
        for record in data:
            key = (record.get('Tarih'), record.get('Oyuncu 1'), record.get('Oyuncu 2'))
            existing_keys.add(key)
        
        added_count = 0
        for record in new_records:
            key = (record.get('Tarih'), record.get('Oyuncu 1'), record.get('Oyuncu 2'))
            if key not in existing_keys:
                record['Sıra'] = get_next_sira(data)
                data.append(record)
                existing_keys.add(key)
                added_count += 1
        
        save_database(data)
        
        return jsonify({
            'success': True,
            'added': added_count,
            'total': len(data),
            'message': f'{added_count} yeni kayıt eklendi'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("🚀 Veritabanı Yönetim Sistemi başlatılıyor...")
    print("📱 Adres: http://localhost:5001")
    print("🛑 Kapatmak için Ctrl+C tuşuna basın\n")
    app.run(debug=True, port=5001)
