# ⚡ Retry Mekanizması - Hızlı Referans

## Başla (Quick Start)

```bash
# Daemon mode'de çalıştır (RECOMMENDED)
python scheduled_pipeline.py --daemon --interval 30

# veya manual çalıştır
python scheduled_pipeline.py --quick
```

## Komutlar

| Komut | Açıklama | Retry |
|-------|----------|-------|
| `--quick` | Hızlı güncelleme | 3 deneme |
| `--full` | Tam güncelleme | 5 deneme |
| `--status` | Durum kontrol | - |
| `--daemon` | Arka planda sürekli | ✅ |

## Çıktı Anlamı

```
✅ BAŞARILI          → Tüm veri çekildi
❌ BAŞARISIZ         → Bazı veri çekilemedi

Retry denemesi: 2    → 2 kez denedi
⚠️  Çekilemeyen: 5   → 5 board hâlâ eksik
```

## Ayarlar

```python
# scheduled_pipeline.py içinde değiştir:

MAX_RETRY_ATTEMPTS = 3  # Deneme sayısı
wait_time = 10          # Max bekleme süresi
```

## Dosyalar

```
📄 RETRY_MECHANISM.md                    (Detaylı belge)
📄 RETRY_IMPLEMENTATION_SUMMARY.md       (Özet)
📄 RETRY_MEKANIZMASI_OZET.md             (Bu özet)
🐍 test_retry_mechanism.py               (Test)
📊 pipeline_status.json                  (Durum)
```

## Sorun Giderme

| Problem | Çözüm |
|---------|-------|
| Veri çekilemiyor | `MAX_RETRY_ATTEMPTS` artır |
| Çok hızlı retry | `wait_time` artır |
| Network hatası | Network kontrol et |

## Mantık

```
Eksik veri var mı?
  ├─ HAYIR → ✅ Tamam
  └─ EVET → Çek
           ├─ Başarılı? → Tekrar kontrol
           ├─ Başarısız? → Bekle & Retry
           └─ Max denemeye ulaştı? → ⚠️ Başarısız
```

---

**Durum:** ✅ Hazır  
**Test:** ✅ Geçti  
**Dokümanı:** ✅ Tamamlandı
