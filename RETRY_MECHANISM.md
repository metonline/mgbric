# Retry Mekanizması - Kapsamlı Belge

## Özet

Pipeline'ın içerisine otomatik **retry mekanizması** entegre edilmiştir. Veri çekme sırasında hiç bir board çekilemezse, sistem otomatik olarak yeniden deneyecek ve tüm veri çekilene kadar devam edecektir.

## Teknik Özellikler

### 1. Quick Update (Periyodik Güncellemeler)

```
Komutu: python scheduled_pipeline.py --quick
Sıklığı: Her 30 dakika
Retry Stratejisi: Hafif
```

**Parametreler:**
- `MAX_RETRY_ATTEMPTS`: 3
- **Backoff Süresi**: 2s → 4s → 8s (max 10s)
- **Timeout Davranışı**: Son denemeden sonra durum kaydedilir

**İş Akışı:**
```
1. Event Registry yenile
2. Veri tutarlılığını kontrol et
3. Event ID hatalarını düzelt
4. Eksik sıralama verileri bul
   └─ Loop (MAX 3):
      ├─ Eksik verileri çek
      ├─ Başarıysanız: ✅ Break
      └─ Başarısızsa: ⏳ Wait → Retry
5. Final kontrol: Hâlâ eksik veri var mı?
6. Status güncelle
```

### 2. Full Update (Tam Güncellemeler)

```
Komutu: python scheduled_pipeline.py --full
Sıklığı: Günlük/Haftalık
Retry Stratejisi: Agresif
```

**Parametreler:**
- `MAX_RETRY_ATTEMPTS`: 5
- **Backoff Süresi**: 2s → 4s → 8s → 16s (max 15s)
- **Detay Seviyesi**: Verbose logging
- **Doğrulama**: Detaylı event ID kontrolü

**İş Akışı:**
```
1. Registry yenile
2. Detaylı doğrulama (orphan results, etc.)
3. Event ID düzeltmeleri
4. Tüm eksik verileri çek
   └─ Loop (MAX 5):
      ├─ Eksik verileri çek
      ├─ Başarıysanız: ✅ Break
      └─ Başarısızsa: ⏳ Wait → Retry
5. Final kontrol + Status güncelle
```

## Veri Yapısı ve Durum Takibi

### Pipeline Status Dosyası (`pipeline_status.json`)

```json
{
  "last_run": "2026-01-24T01:30:00",
  "last_success": "2026-01-24T01:18:34",
  "total_runs": 10,
  "total_boards_fetched": 350,
  "unfetched_boards": {
    "event_id_123": [4, 8, 12],
    "event_id_456": [1, 7]
  },
  "errors": [
    {
      "timestamp": "2026-01-24T01:20:00",
      "error": ["2 board çekilemedi (3 deneme sonrası)"]
    }
  ]
}
```

### Çıktı Sonuç Formatı

**Başarılı:**
```
✅ BAŞARILI
Çekilen board: 15
Düzeltilen event ID: 2
Retry denemesi: 2
```

**Başarısız:**
```
❌ BAŞARISIZ
Çekilen board: 10
Düzeltilen event ID: 1
Retry denemesi: 3
⚠️  Çekilemeyen board: 5
Hatalar: ['5 board çekilemedi (3 deneme sonrası)']
```

## Log Mesajleri Açıklaması

### Normal Çalışma

| Log | Anlamı |
|-----|--------|
| `📊 Çekiliş #1: 20 event, 150 eksik board` | İlk deneme, bu kadar veri eksik |
| `✓ 45 board çekildi` | Bu denemede başarılı sayı |
| `⏳ 2s sonra yeniden deneyelim...` | Backoff başlıyor |
| `✅ Tüm veri başarılı şekilde çekildi` | Tamamlandı, break! |

### Hata Durumları

| Log | Anlamı |
|-----|--------|
| `⚠️  Hiç board çekilemedi - retry gerekiyor` | 0 başarı, retry yapılacak |
| `⚠️  3 event'de 5 board hâlâ eksik` | Final kontrol sonucu |
| `❌ Quick update hatası: ...` | İstisnai hata |

## Test Etme

### 1. Normal Çalışmayı Doğrula

```bash
# Hiç veri eksik değilse
python scheduled_pipeline.py --quick

# Çıktı:
# 📊 Çekiliş #1: 0 event, 0 eksik board bulundu
# ✅ Tüm veri başarılı şekilde çekildi
# Quick update tamamlandı: 0 board çekildi (1 deneme)
```

### 2. Retry Mekanizmasını Simüle Et

```bash
# Test script'ini çalıştır
python test_retry_mechanism.py

# Bu, test senaryolarını hazırlar:
# - Senaryo 1: Eksik veri yok
# - Senaryo 2: Veri eksikliği → Retry
# - Senaryo 3: Çok fazla eksik → MAX_RETRY
```

### 3. Manuel Test

```python
# unified_fetch.py içinde fetch_missing_rankings() 
# fonksiyonunu debug edebilirsiniz

# Veya:
python scheduled_pipeline.py --full

# Logging'i gözlemleyin ve retry denemeleri takip edin
```

## Yapılandırma (Özelleştirme)

### Quick Update Retry Ayarları

[scheduled_pipeline.py](scheduled_pipeline.py) içinde:
```python
MAX_RETRY_ATTEMPTS = 3  # Değiştir: 3 → 5
wait_time = min(10, 2 ** retry_count)  # Değiştir: 10 → 20
```

### Full Update Retry Ayarları

Aynı dosyada:
```python
MAX_RETRY_ATTEMPTS = 5  # Değiştir: 5 → 8
wait_time = min(15, 2 ** retry_count)  # Değiştir: 15 → 30
```

### Backoff Stratejisi Değişikliği

Exponential backoff yerine linear:
```python
# Şu:
wait_time = min(10, 2 ** retry_count)

# Yerine:
wait_time = min(10, retry_count * 2)  # 2s, 4s, 6s, 8s, 10s
```

## Günlük Operasyon

### Otomatik Yürütme (Daemon Mode)

```bash
python scheduled_pipeline.py --daemon --interval 30
```

- Her 30 dakikada quick update çalışır
- Retry mekanizması otomatik çalışır
- Hiç müdahale gerektirmez

### Manuel Çalıştırma

```bash
# Hızlı güncelleme
python scheduled_pipeline.py --quick

# Tam güncelleme
python scheduled_pipeline.py --full

# Durum kontrol
python scheduled_pipeline.py --status
```

### Durum Kontrol

```bash
python scheduled_pipeline.py --status

# Çıktı:
# ==================================================
# PIPELINE STATUS
# ==================================================
# Son çalışma: 2026-01-24T01:30:00
# Son başarılı: 2026-01-24T01:30:00
# Toplam çalışma: 10
# Toplam board çekildi: 345
# Son hatalar: 0
# ==================================================
```

## Sorun Giderme

### Veri Hâlâ Çekilemiyorsa

1. **Network Bağlantısını Kontrol Et**
   ```bash
   ping bridgewebs.com
   # veya
   python -c "import requests; requests.get('https://www.bridgewebs.com')"
   ```

2. **Retry Denemelerini Artır**
   ```python
   # scheduled_pipeline.py içinde:
   MAX_RETRY_ATTEMPTS = 5  # 3'ten 5'e artır
   ```

3. **Backoff Süresini Artır**
   ```python
   # Yavaşladığı için API rate limit?
   wait_time = min(30, 2 ** retry_count)  # 10'dan 30'a artır
   ```

4. **Detaylı Log'u Kontrol Et**
   ```bash
   python scheduled_pipeline.py --full  # Daha detaylı output
   ```

### Çok Fazla Retry Hatası

1. **Hedef kaynağı kontrol et** (BridgeWebs API accessibility)
2. **Event registry'yi temizle**
3. **Başaçıl bir full update çalıştır**

## Özet

| Özellik | Quick | Full |
|---------|-------|------|
| Max Retry | 3 | 5 |
| Backoff | 2-10s | 2-15s |
| Sıklık | 30 dakika | Günlük |
| Detay | Hafif | Yoğun |
| **Amaç** | İnkremental | Tam validasyon |

---

## Dosya Referansları

- **Ana Implementation**: [scheduled_pipeline.py](scheduled_pipeline.py)
  - `run_quick_update()`: Hızlı güncelleme retry mekanizması
  - `run_full_update()`: Tam güncelleme retry mekanizması
  - Satırlar: ~100-200 (quick), ~210-280 (full)

- **Test Script**: [test_retry_mechanism.py](test_retry_mechanism.py)
  - Retry mekanizmasını test etmek için senaryolar
  - Database yedekleme/geri yükleme işlevleri

- **Veri Fetcher**: [unified_fetch.py](unified_fetch.py#L401-L470)
  - `get_missing_rankings()`: Çekilemeyen verileri bul
  - `fetch_missing_rankings()`: Verileri çek

- **Status Dosyası**: `pipeline_status.json`
  - Retry denemelerinin sonuçlarını içerir
  - `unfetched_boards` alanı çekilemeyen board'ları gösterir
