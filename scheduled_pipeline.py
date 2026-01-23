#!/usr/bin/env python3
"""
Scheduled Pipeline - Periyodik veri güncelleme işlemleri

Bu script Windows Task Scheduler veya cron ile çalıştırılabilir.
Tüm veri işlemlerini tek noktadan yönetir.

Kullanım:
    python scheduled_pipeline.py              # Tam güncelleme
    python scheduled_pipeline.py --quick      # Hızlı güncelleme (sadece eksikler)
    python scheduled_pipeline.py --rankings   # Sadece sıralama verileri
    python scheduled_pipeline.py --daemon     # Daemon modu (30 dk aralık)
    
Windows Task Scheduler için:
    Trigger: Her 30 dakikada bir
    Action: python.exe scheduled_pipeline.py --quick
    Start in: C:\\Users\\metin\\Desktop\\BRIC
"""

import json
import sys
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Setup logging
LOG_FILE = Path(__file__).parent / "pipeline.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Local imports
try:
    from event_registry import EventRegistry
    from unified_fetch import DataFetcher
except ImportError as e:
    logger.error(f"Import hatası: {e}")
    sys.exit(1)


class ScheduledPipeline:
    """
    Periyodik veri güncelleme pipeline'ı
    
    Workflow:
    1. Veri tutarlılığını kontrol et
    2. Event ID tutarsızlıklarını düzelt
    3. Eksik sıralama verilerini çek
    4. Sonuçları logla
    """
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.status_file = self.base_path / "pipeline_status.json"
        self.registry = EventRegistry()
        
    def load_status(self) -> dict:
        """Son çalışma durumunu yükle"""
        try:
            with open(self.status_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {
                "last_run": None,
                "last_success": None,
                "total_runs": 0,
                "total_boards_fetched": 0,
                "errors": []
            }
    
    def save_status(self, status: dict):
        """Çalışma durumunu kaydet"""
        with open(self.status_file, 'w', encoding='utf-8') as f:
            json.dump(status, f, ensure_ascii=False, indent=2)
    
    def run_quick_update(self) -> dict:
        """
        Hızlı güncelleme - sadece eksik verileri çeker
        30 dakikalık periyodik çalışma için optimize edilmiş
        """
        logger.info("=" * 60)
        logger.info("QUICK UPDATE BAŞLADI")
        logger.info("=" * 60)
        
        result = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "boards_fetched": 0,
            "event_ids_fixed": 0,
            "errors": []
        }
        
        try:
            # 1. Event Registry'yi yenile
            logger.info("Event Registry yenileniyor...")
            self.registry.reload()
            
            # 2. Veri tutarlılığını kontrol et
            logger.info("Veri tutarlılığı kontrol ediliyor...")
            fetcher = DataFetcher(verbose=False)
            issues = fetcher.validate_data()
            
            # 3. Event ID tutarsızlıklarını düzelt
            if issues['hands_event_id_issues']:
                logger.warning(f"{len(issues['hands_event_id_issues'])} event ID tutarsızlığı bulundu, düzeltiliyor...")
                fixed = fetcher.fix_event_ids(dry_run=False)
                result['event_ids_fixed'] = fixed
            
            # 4. Eksik sıralama verilerini çek
            missing = fetcher.get_missing_rankings()
            total_missing = sum(len(boards) for boards in missing.values())
            
            if total_missing > 0:
                logger.info(f"{len(missing)} event, {total_missing} eksik board bulundu")
                fetched = fetcher.fetch_missing_rankings()
                result['boards_fetched'] = fetched
            else:
                logger.info("Eksik veri yok")
            
            # 5. Sonuç
            logger.info(f"Quick update tamamlandı: {result['boards_fetched']} board çekildi")
            
        except Exception as e:
            logger.error(f"Quick update hatası: {e}")
            result['success'] = False
            result['errors'].append(str(e))
        
        # Status güncelle
        status = self.load_status()
        status['last_run'] = result['timestamp']
        status['total_runs'] += 1
        status['total_boards_fetched'] += result['boards_fetched']
        if result['success']:
            status['last_success'] = result['timestamp']
        else:
            status['errors'].append({
                "timestamp": result['timestamp'],
                "error": result['errors']
            })
            # Son 10 hatayı tut
            status['errors'] = status['errors'][-10:]
        self.save_status(status)
        
        return result
    
    def run_full_update(self) -> dict:
        """
        Tam güncelleme - tüm verileri kontrol eder ve günceller
        Günlük veya haftalık çalışma için
        """
        logger.info("=" * 60)
        logger.info("FULL UPDATE BAŞLADI")
        logger.info("=" * 60)
        
        result = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "boards_fetched": 0,
            "event_ids_fixed": 0,
            "validation_report": {},
            "errors": []
        }
        
        try:
            # 1. Registry kontrolü
            logger.info("Event Registry kontrol ediliyor...")
            self.registry.reload()
            
            # 2. Detaylı doğrulama
            logger.info("Detaylı doğrulama yapılıyor...")
            fetcher = DataFetcher(verbose=True)
            issues = fetcher.validate_data()
            result['validation_report'] = {
                'event_id_issues': len(issues['hands_event_id_issues']),
                'missing_boards': sum(len(x['boards']) for x in issues['missing_board_results']),
                'orphan_results': len(issues['orphan_board_results'])
            }
            
            # 3. Düzeltmeler
            if issues['hands_event_id_issues']:
                logger.info(f"{len(issues['hands_event_id_issues'])} event ID düzeltiliyor...")
                result['event_ids_fixed'] = fetcher.fix_event_ids(dry_run=False)
            
            # 4. Tüm eksik verileri çek
            if result['validation_report']['missing_boards'] > 0:
                logger.info(f"{result['validation_report']['missing_boards']} eksik board çekiliyor...")
                result['boards_fetched'] = fetcher.fetch_missing_rankings()
            
            logger.info("Full update tamamlandı")
            
        except Exception as e:
            logger.error(f"Full update hatası: {e}")
            result['success'] = False
            result['errors'].append(str(e))
        
        # Status güncelle
        status = self.load_status()
        status['last_run'] = result['timestamp']
        status['last_full_update'] = result['timestamp']
        status['total_runs'] += 1
        status['total_boards_fetched'] += result['boards_fetched']
        if result['success']:
            status['last_success'] = result['timestamp']
        self.save_status(status)
        
        return result
    
    def run_daemon(self, interval_minutes: int = 30):
        """
        Daemon modu - sürekli çalışır ve periyodik güncelleme yapar
        """
        logger.info(f"Daemon modu başlatıldı. Aralık: {interval_minutes} dakika")
        
        while True:
            try:
                self.run_quick_update()
            except Exception as e:
                logger.error(f"Daemon döngü hatası: {e}")
            
            logger.info(f"Sonraki çalışma: {interval_minutes} dakika sonra")
            time.sleep(interval_minutes * 60)
    
    def get_status_summary(self) -> str:
        """Durum özeti döndür"""
        status = self.load_status()
        
        lines = [
            "=" * 50,
            "PIPELINE STATUS",
            "=" * 50,
            f"Son çalışma: {status.get('last_run', 'Hiç')}",
            f"Son başarılı: {status.get('last_success', 'Hiç')}",
            f"Toplam çalışma: {status.get('total_runs', 0)}",
            f"Toplam board: {status.get('total_boards_fetched', 0)}",
            f"Son hatalar: {len(status.get('errors', []))}",
            "=" * 50
        ]
        
        return "\n".join(lines)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Scheduled Pipeline')
    parser.add_argument('--quick', action='store_true', help='Hızlı güncelleme')
    parser.add_argument('--full', action='store_true', help='Tam güncelleme')
    parser.add_argument('--rankings', action='store_true', help='Sadece sıralama verileri')
    parser.add_argument('--daemon', action='store_true', help='Daemon modu')
    parser.add_argument('--interval', type=int, default=30, help='Daemon aralığı (dakika)')
    parser.add_argument('--status', action='store_true', help='Durum göster')
    
    args = parser.parse_args()
    
    pipeline = ScheduledPipeline()
    
    if args.status:
        print(pipeline.get_status_summary())
        return
    
    if args.daemon:
        pipeline.run_daemon(args.interval)
        return
    
    if args.full:
        result = pipeline.run_full_update()
    else:
        # Default: quick update
        result = pipeline.run_quick_update()
    
    # Sonuç özeti
    print(f"\nSonuç: {'BAŞARILI' if result['success'] else 'BAŞARISIZ'}")
    print(f"Çekilen board: {result['boards_fetched']}")
    print(f"Düzeltilen event ID: {result['event_ids_fixed']}")
    if result['errors']:
        print(f"Hatalar: {result['errors']}")


if __name__ == "__main__":
    main()
