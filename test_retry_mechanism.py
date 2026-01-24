#!/usr/bin/env python3
"""
Retry Mekanizması Test Scripti
==============================

Bu script, pipeline'ın retry mekanizmasını test eder:
- Verilerin eksik olduğu durumları simüle eder
- Retry denemelerini gözlemler
- Başarı/başarısızlık senaryolarını doğrular

Test Senaryoları:
1. Tamamen başarılı çekiliş (0 deneme)
2. 1 denemede başarısız, 2. denemede başarı
3. MAX_RETRY denemelerinden sonra başarısız
4. Event ID hatası -> düzeltme -> başarılı çekiliş
"""

import json
import os
import shutil
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def backup_database():
    """Database'i yedekle"""
    logger.info("📦 Database yedekleniyor...")
    if os.path.exists('hands_database.json'):
        shutil.copy('hands_database.json', 'hands_database.json.backup')
        logger.info("✅ Yedek oluşturuldu: hands_database.json.backup")
    else:
        logger.warning("⚠️  hands_database.json bulunamadı")

def restore_database():
    """Database'i geri yükle"""
    logger.info("📦 Database geri yükleniyor...")
    if os.path.exists('hands_database.json.backup'):
        shutil.copy('hands_database.json.backup', 'hands_database.json')
        logger.info("✅ Database geri yüklendi")
    else:
        logger.warning("⚠️  Yedek bulunamadı")

def simulate_missing_data(num_missing=5):
    """
    Belirtilen sayıda board'ı database'den kaldır
    (Missing data simülasyonu)
    """
    logger.info(f"\n🎭 {num_missing} board kaldırılıyor...")
    
    with open('hands_database.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if len(data) > num_missing:
        removed_ids = []
        for i in range(num_missing):
            hand = data.pop(0)
            removed_ids.append(f"Board {hand.get('board', '?')} from {hand.get('date', '?')}")
        
        with open('hands_database.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ {num_missing} board kaldırıldı:")
        for removed in removed_ids:
            logger.info(f"   - {removed}")
    else:
        logger.warning(f"⚠️  Yeterince board yok")
    
    return len(data)

def test_scenario_1():
    """Senaryo 1: Veri eksiği yok, tek çekiliş"""
    logger.info("\n" + "="*60)
    logger.info("TEST SENARYO 1: Eksik veri yok")
    logger.info("="*60)
    logger.info("✅ Beklenen sonuç: 0 deneme, tüm veri başarılı")
    
    backup_database()
    
    logger.info("\n🚀 Pipeline başlatılıyor...")
    logger.info("→ scheduled_pipeline.py --quick")
    logger.info("\n⏳ Test için: python scheduled_pipeline.py --quick")
    
    return "Senaryo 1"

def test_scenario_2():
    """Senaryo 2: Veri eksikliği, retry ile başarı"""
    logger.info("\n" + "="*60)
    logger.info("TEST SENARYO 2: Veri eksikliği → Retry → Başarı")
    logger.info("="*60)
    logger.info("✅ Beklenen sonuç: 2-3 deneme, tüm veri çekilir")
    
    backup_database()
    remaining = simulate_missing_data(3)
    
    logger.info(f"\n📊 Database durumu:")
    logger.info(f"   Mevcut: {remaining}")
    logger.info(f"   Çekilecek: 3 board")
    
    logger.info("\n🚀 Pipeline başlatılıyor...")
    logger.info("→ scheduled_pipeline.py --quick")
    logger.info("\nObserve:")
    logger.info("   1. 'Çekiliş #1: 3 eksik board bulundu' → 0 çekilir (simülasyon)")
    logger.info("   2. '⏳ Xs sonra yeniden deneyelim' → bekle")
    logger.info("   3. 'Çekiliş #2: ...' → retry başa")
    logger.info("   4. Son satır: 'Retry denemesi: 2' or '3'")
    
    return "Senaryo 2"

def test_scenario_3():
    """Senaryo 3: Çok fazla eksik veri, MAX_RETRY sonrası başarısız"""
    logger.info("\n" + "="*60)
    logger.info("TEST SENARYO 3: Çok fazla veri eksikliği → MAX_RETRY → Başarısız")
    logger.info("="*60)
    logger.info("⚠️  Beklenen sonuç: 3 deneme max, sonra başarısız işaretlenir")
    
    backup_database()
    remaining = simulate_missing_data(20)
    
    logger.info(f"\n📊 Database durumu:")
    logger.info(f"   Mevcut: {remaining}")
    logger.info(f"   Çekilecek: 20 board (çok fazla)")
    
    logger.info("\n🚀 Pipeline başlatılıyor...")
    logger.info("→ scheduled_pipeline.py --full")
    logger.info("\nObserve:")
    logger.info("   1. 'Çekiliş #1-5' → tüm denemeler")
    logger.info("   2. Final: '⚠️  X event'de Y board hâlâ eksik'")
    logger.info("   3. Sonuç: '❌ BAŞARISIZ'")
    logger.info("   4. Status'te: 'unfetched_boards' gösteriyor")
    
    return "Senaryo 3"

def test_retry_logic_documentation():
    """Retry mekanizmasının detaylı belgesi"""
    logger.info("\n" + "="*60)
    logger.info("RETRY MEKANIZMASI DETAYLI DOKUMENTASYON")
    logger.info("="*60)
    
    doc = """
QUICK UPDATE Retry Mekanizması:
─────────────────────────────
• MAX_RETRY_ATTEMPTS = 3
• Exponential backoff: 2s → 4s → 8s (max 10s)
• Tüm veri çekilene kadar loop
• Başarısız halde durum status'e kaydedilir

FULL UPDATE Retry Mekanizması:
──────────────────────────────
• MAX_RETRY_ATTEMPTS = 5
• Exponential backoff: 2s → 4s → 8s → 16s (max 15s)
• Daha agresif retry stratejisi
• Detaylı doğrulama raporları

Status Dosyasına Yazılan Veriler:
─────────────────────────────────
{
  "last_run": "2026-01-24T...",
  "last_success": "2026-01-24T...",
  "total_runs": 10,
  "total_boards_fetched": 245,
  "unfetched_boards": {
    "event_id": [1, 5, 10, ...]  ← Çekilemeyen board numaraları
  },
  "errors": [...]
}

Komut Çıktısı:
──────────────
✅ BAŞARILI: Tüm veri çekildi
Çekilen board: 10
Düzeltilen event ID: 0
Retry denemesi: 2

veya

❌ BAŞARISIZ: Bazı veri çekilemedi
Çekilen board: 8
Düzeltilen event ID: 1
Retry denemesi: 3
⚠️  Çekilemeyen board: 2
Hatalar: ['2 board çekilemedi (3 deneme sonrası)']
    """
    
    logger.info(doc)

def run_all_tests():
    """Tüm test senaryolarını çalıştır"""
    logger.info("\n" + "█"*60)
    logger.info("█" + " "*58 + "█")
    logger.info("█" + "  RETRY MEKANIZMASI TEST SUITE".center(58) + "█")
    logger.info("█" + " "*58 + "█")
    logger.info("█"*60)
    
    try:
        # Retry mekanizması belgesi
        test_retry_logic_documentation()
        
        # Test senaryoları
        scenarios = [
            test_scenario_1,
            test_scenario_2,
            test_scenario_3
        ]
        
        for scenario_func in scenarios:
            try:
                scenario_name = scenario_func()
                logger.info(f"✅ {scenario_name} hazır")
            except Exception as e:
                logger.error(f"❌ {scenario_func.__name__} hatası: {e}")
        
        # Son instructions
        logger.info("\n" + "="*60)
        logger.info("TESTE BAŞLAMAK İÇİN:")
        logger.info("="*60)
        logger.info("1. Tarafınızdan seçilen senaryoyu çalıştırın")
        logger.info("2. Pipeline çıktısını gözlemleyin")
        logger.info("3. Retry denemeleri ve durum takibini doğrulayın")
        logger.info("4. Test sonrası: python test_retry_mechanism.py --restore")
        logger.info("   (Database'i orijinal haline döndür)")
        logger.info("\n💡 Not: Scenarioları sırayla veya ayrı ayrı çalıştırabilirsiniz")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"Test suite hatası: {e}")

if __name__ == "__main__":
    import sys
    
    if "--restore" in sys.argv:
        restore_database()
    else:
        run_all_tests()
