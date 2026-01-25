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
import re
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
        
        RETRY MEKANIZMASI: Tüm veri çekilene kadar yeniden deneyin
        - MAX 3 deneme
        - Exponential backoff (2s, 4s, 8s)
        - Tüm eksik board çekilene kadar devam et
        """
        logger.info("=" * 60)
        logger.info("QUICK UPDATE BAŞLADI")
        logger.info("=" * 60)
        
        result = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "boards_fetched": 0,
            "hands_fetched": 0,
            "event_ids_fixed": 0,
            "unfetched_boards": {},
            "retry_attempts": 0,
            "errors": []
        }
        
        MAX_RETRY_ATTEMPTS = 3
        retry_count = 0
        
        try:
            # 0. Vugraph calendar'dan yeni event'leri getir ve kaydet
            logger.info("\n📅 Vugraph calendar'dan yeni event'leri tarayıyor...")
            try:
                import requests
                from bs4 import BeautifulSoup
                
                BASE_URL = "https://clubs.vugraph.com/hosgoru"
                response = requests.get(f"{BASE_URL}/calendar.php", timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Load current database to update
                with open(self.base_path / 'database.json', 'r', encoding='utf-8') as f:
                    db = json.load(f)
                
                if 'events' not in db:
                    db['events'] = {}
                
                new_events_count = 0
                # Find all calendar event links
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    if 'eventresults.php' in href:
                        match = re.search(r'event=(\d+)', href)
                        if match:
                            event_id = str(match.group(1))
                            # Check if already in registry
                            if event_id not in db['events']:
                                # Fetch event details to get actual date
                                event_date = 'unknown'
                                event_name = 'New Event from Calendar'
                                try:
                                    event_response = requests.get(f"{BASE_URL}/eventresults.php?event={event_id}", timeout=10)
                                    event_soup = BeautifulSoup(event_response.content, 'html.parser')
                                    # Look for date in headers like "PAZAR Sonuçları (18-01-2026 14:00)"
                                    for header in event_soup.find_all(['h1', 'h2', 'h3']):
                                        header_text = header.get_text()
                                        # Extract date in format DD-MM-YYYY or DD.MM.YYYY
                                        date_match = re.search(r'(\d{1,2})[-.]?(\d{1,2})[-.]?(\d{4})', header_text)
                                        if date_match:
                                            day, month, year = date_match.groups()
                                            event_date = f"{day}.{month}.{year}"
                                            event_name = header_text.strip()
                                            break
                                except Exception:
                                    pass  # Keep unknown date if fetch fails
                                
                                db['events'][event_id] = {
                                    'id': event_id,
                                    'date': event_date,
                                    'name': event_name
                                }
                                new_events_count += 1
                
                if new_events_count > 0:
                    logger.info(f"  ✓ {new_events_count} yeni event bulundu")
                    # Save updated database
                    with open(self.base_path / 'database.json', 'w', encoding='utf-8') as f:
                        json.dump(db, f, ensure_ascii=False, indent=2)
                    logger.info(f"  ✓ database.json güncellendi")
                else:
                    logger.info(f"  ✓ Yeni event yok")
            except Exception as e:
                logger.warning(f"⚠️  Calendar taraması hatası: {e}")
            
            # 1. Event Registry'yi yenile
            logger.info("\nEvent Registry yenileniyor...")
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
            
            # 4. Yeni eventler için hands verileri çek
            logger.info("\n📂 Yeni eventler için hands verilerini çek...")
            try:
                hands_event_ids = set()
                with open(self.base_path / 'hands_database.json', 'r', encoding='utf-8') as f:
                    hands_data = json.load(f)
                    hands_event_ids = set(h.get('event_id') for h in hands_data if h.get('event_id'))
                
                all_event_ids = set(self.registry._event_to_date.keys())
                new_events = all_event_ids - hands_event_ids
                
                if new_events:
                    logger.info(f"🔍 {len(new_events)} yeni event bulundu")
                    hands_fetched = 0
                    event_count = 0
                    hands_saved = False
                    for event_id in sorted(new_events):
                        date = self.registry._event_to_date.get(event_id, 'N/A')
                        # SKIP non-2026 events
                        if not date.endswith('.2026'):
                            continue
                        event_count += 1
                        if event_count > 20:
                            break
                        logger.info(f"  Hands çekiliyor: Event {event_id} ({date})")
                        try:
                            hands = fetcher.fetch_hands_for_event(event_id)
                            if hands:
                                hands_fetched += len(hands)
                                # Add hands to database
                                for hand in hands:
                                    # Set date field if not present
                                    if 'date' not in hand and 'Tarih' in hand:
                                        hand['date'] = hand['Tarih']
                                    hands_data.append(hand)
                                hands_saved = True
                                logger.info(f"    ✓ {len(hands)} el çekildi")
                        except Exception as e:
                            logger.warning(f"    ⚠️  Hands çekme hatası: {e}")
                    
                    # Save hands_data if new hands were added
                    if hands_saved:
                        with open(self.base_path / 'hands_database.json', 'w', encoding='utf-8') as f:
                            json.dump(hands_data, f, ensure_ascii=False, indent=2)
                        logger.info(f"  ✓ Hands veritabanı kaydedildi ({len(hands_data)} toplam el)")
                    
                    result['hands_fetched'] = hands_fetched
                else:
                    logger.info("  ✓ Yeni event yok")
            except Exception as e:
                logger.warning(f"⚠️  Yeni event taraması hatası: {e}")
            
            # 5. Eksik sıralama verilerini RETRY MEKANIZMASI ile çek
            while retry_count < MAX_RETRY_ATTEMPTS:
                missing = fetcher.get_missing_rankings()
                total_missing = sum(len(boards) for boards in missing.values())
                
                if total_missing == 0:
                    logger.info("✅ Tüm veri başarılı şekilde çekildi")
                    break
                
                logger.info(f"\n📊 Çekiliş #{retry_count + 1}: {len(missing)} event, {total_missing} eksik board bulundu")
                
                # Eksik verileri çek
                fetched = fetcher.fetch_missing_rankings()
                result['boards_fetched'] += fetched
                
                if fetched > 0:
                    logger.info(f"✓ {fetched} board çekildi")
                else:
                    logger.warning("⚠️  Hiç board çekilemedi - retry gerekiyor")
                
                retry_count += 1
                
                # Son denemeden sonra bekle
                if retry_count < MAX_RETRY_ATTEMPTS and total_missing > 0 and fetched == 0:
                    wait_time = min(10, 2 ** retry_count)  # Exponential backoff
                    logger.info(f"⏳ {wait_time}s sonra yeniden deneyelim...")
                    time.sleep(wait_time)
            
            # Son eksik veri kontrolü
            final_missing = fetcher.get_missing_rankings()
            if final_missing:
                final_total = sum(len(boards) for boards in final_missing.values())
                logger.warning(f"⚠️  {len(final_missing)} event'de {final_total} board hâlâ eksik")
                result['unfetched_boards'] = final_missing
                if final_total > 0:
                    result['success'] = False
                    result['errors'].append(f"{final_total} board çekilemedi ({MAX_RETRY_ATTEMPTS} deneme sonrası)")
            
            result['retry_attempts'] = retry_count
            
            # 5. Board rankings otomatik olarak generate et
            logger.info("\n🏆 Board rankings otomatik olarak generate ediliyor...")
            try:
                from generate_board_rankings import BoardRankingsGenerator
                generator = BoardRankingsGenerator()
                if generator.generate_all():
                    logger.info("✅ Board rankings başarılı şekilde generate edildi")
                else:
                    logger.warning("⚠️  Board rankings generate edilirken hata")
            except Exception as e:
                logger.warning(f"⚠️  Board rankings hatası: {e}")
            
            # 6. Sonuç
            logger.info(f"\n✅ Quick update tamamlandı: {result['boards_fetched']} board çekildi ({retry_count} deneme)")
            
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
        
        # Çekilemeyen verileri status'e kaydet
        if result['unfetched_boards']:
            status['unfetched_boards'] = result['unfetched_boards']
        else:
            status.pop('unfetched_boards', None)
        
        self.save_status(status)
        
        return result
    
    def run_full_update(self) -> dict:
        """
        Tam güncelleme - tüm verileri kontrol eder ve günceller
        Günlük veya haftalık çalışma için
        
        RETRY MEKANIZMASI: MAX 5 deneme ile tüm veriyi çekmeye çalış
        """
        logger.info("=" * 60)
        logger.info("FULL UPDATE BAŞLADI")
        logger.info("=" * 60)
        
        result = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "boards_fetched": 0,
            "hands_fetched": 0,
            "event_ids_fixed": 0,
            "validation_report": {},
            "unfetched_boards": {},
            "retry_attempts": 0,
            "errors": []
        }
        
        MAX_RETRY_ATTEMPTS = 5
        retry_count = 0
        
        try:
            # 0. Vugraph calendar'dan yeni event'leri getir ve kaydet
            logger.info("\n📅 Vugraph calendar'dan yeni event'leri tarayıyor...")
            try:
                import requests
                from bs4 import BeautifulSoup
                
                BASE_URL = "https://clubs.vugraph.com/hosgoru"
                response = requests.get(f"{BASE_URL}/calendar.php", timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Load current database to update
                with open(self.base_path / 'database.json', 'r', encoding='utf-8') as f:
                    db = json.load(f)
                
                if 'events' not in db:
                    db['events'] = {}
                
                new_events_count = 0
                # Find all calendar event links
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    if 'eventresults.php' in href:
                        match = re.search(r'event=(\d+)', href)
                        if match:
                            event_id = str(match.group(1))
                            # Check if already in registry
                            if event_id not in db['events']:
                                # Fetch event details to get actual date
                                event_date = 'unknown'
                                event_name = 'New Event from Calendar'
                                try:
                                    event_response = requests.get(f"{BASE_URL}/eventresults.php?event={event_id}", timeout=10)
                                    event_soup = BeautifulSoup(event_response.content, 'html.parser')
                                    # Look for date in headers like "PAZAR Sonuçları (18-01-2026 14:00)"
                                    for header in event_soup.find_all(['h1', 'h2', 'h3']):
                                        header_text = header.get_text()
                                        # Extract date in format DD-MM-YYYY or DD.MM.YYYY
                                        date_match = re.search(r'(\d{1,2})[-.]?(\d{1,2})[-.]?(\d{4})', header_text)
                                        if date_match:
                                            day, month, year = date_match.groups()
                                            event_date = f"{day}.{month}.{year}"
                                            event_name = header_text.strip()
                                            break
                                except Exception:
                                    pass  # Keep unknown date if fetch fails
                                
                                db['events'][event_id] = {
                                    'id': event_id,
                                    'date': event_date,
                                    'name': event_name
                                }
                                new_events_count += 1
                
                if new_events_count > 0:
                    logger.info(f"  ✓ {new_events_count} yeni event bulundu")
                    # Save updated database
                    with open(self.base_path / 'database.json', 'w', encoding='utf-8') as f:
                        json.dump(db, f, ensure_ascii=False, indent=2)
                    logger.info(f"  ✓ database.json güncellendi")
                else:
                    logger.info(f"  ✓ Yeni event yok")
            except Exception as e:
                logger.warning(f"⚠️  Calendar taraması hatası: {e}")
            
            # 1. Registry kontrolü
            logger.info("\nEvent Registry kontrol ediliyor...")
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
            
            # 4. Yeni eventler için hands verileri çek
            logger.info("\n📂 Yeni eventler için hands verilerini çek (2026+ only)...")
            try:
                hands_event_ids = set()
                with open(self.base_path / 'hands_database.json', 'r', encoding='utf-8') as f:
                    hands_data = json.load(f)
                    hands_event_ids = set(h.get('event_id') for h in hands_data if h.get('event_id'))
                
                all_event_ids = set(self.registry._event_to_date.keys())
                new_events = all_event_ids - hands_event_ids
                
                if new_events:
                    logger.info(f"🔍 {len(new_events)} yeni event bulundu")
                    hands_fetched = 0
                    event_count = 0
                    hands_saved = False
                    for event_id in sorted(new_events):
                        date = self.registry._event_to_date.get(event_id, 'N/A')
                        # SKIP non-2026 events
                        if not date.endswith('.2026'):
                            continue
                        event_count += 1
                        logger.info(f"  Hands çekiliyor: Event {event_id} ({date})")
                        try:
                            hands = fetcher.fetch_hands_for_event(event_id)
                            if hands:
                                hands_fetched += len(hands)
                                # Add hands to database
                                for hand in hands:
                                    # Set date field if not present
                                    if 'date' not in hand and 'Tarih' in hand:
                                        hand['date'] = hand['Tarih']
                                    hands_data.append(hand)
                                hands_saved = True
                                logger.info(f"    ✓ {len(hands)} el çekildi")
                        except Exception as e:
                            logger.warning(f"    ⚠️  Hands çekme hatası: {e}")
                    
                    # Save hands_data if new hands were added
                    if hands_saved:
                        with open(self.base_path / 'hands_database.json', 'w', encoding='utf-8') as f:
                            json.dump(hands_data, f, ensure_ascii=False, indent=2)
                        logger.info(f"  ✓ Hands veritabanı kaydedildi ({len(hands_data)} toplam el)")
                    
                    result['hands_fetched'] = hands_fetched
                else:
                    logger.info("  ✓ Yeni event yok")
            except Exception as e:
                logger.warning(f"⚠️  Yeni event taraması hatası: {e}")
            
            # 5. Tüm eksik verileri RETRY MEKANIZMASI ile çek
            while retry_count < MAX_RETRY_ATTEMPTS:
                missing = fetcher.get_missing_rankings()
                total_missing = sum(len(boards) for boards in missing.values())
                
                if total_missing == 0:
                    logger.info("✅ Tüm veri başarılı şekilde çekildi")
                    break
                
                logger.info(f"\n📊 Çekiliş #{retry_count + 1}: {len(missing)} event, {total_missing} eksik board")
                
                # Tüm eksik verileri çek
                fetched = fetcher.fetch_missing_rankings()
                result['boards_fetched'] += fetched
                
                if fetched > 0:
                    logger.info(f"✓ {fetched} board çekildi")
                else:
                    logger.warning("⚠️  Hiç board çekilemedi - retry gerekiyor")
                
                retry_count += 1
                
                # Son denemeden sonra bekle (exponential backoff)
                if retry_count < MAX_RETRY_ATTEMPTS and total_missing > 0 and fetched == 0:
                    wait_time = min(15, 2 ** retry_count)
                    logger.info(f"⏳ {wait_time}s sonra yeniden deneyelim...")
                    time.sleep(wait_time)
            
            # Son eksik veri kontrolü
            final_missing = fetcher.get_missing_rankings()
            if final_missing:
                final_total = sum(len(boards) for boards in final_missing.values())
                logger.warning(f"⚠️  {len(final_missing)} event'de {final_total} board hâlâ eksik")
                result['unfetched_boards'] = final_missing
                if final_total > 0:
                    result['success'] = False
                    result['errors'].append(f"{final_total} board çekilemedi ({MAX_RETRY_ATTEMPTS} deneme sonrası)")
            
            result['retry_attempts'] = retry_count
            
            # 6. Board rankings otomatik olarak generate et
            logger.info("\n🏆 Board rankings otomatik olarak generate ediliyor...")
            try:
                from generate_board_rankings import BoardRankingsGenerator
                generator = BoardRankingsGenerator()
                if generator.generate_all():
                    logger.info("✅ Board rankings başarılı şekilde generate edildi")
                else:
                    logger.warning("⚠️  Board rankings generate edilirken hata")
            except Exception as e:
                logger.warning(f"⚠️  Board rankings hatası: {e}")
            
            logger.info(f"\n✅ Full update tamamlandı: {result['boards_fetched']} board çekildi ({retry_count} deneme)")
            
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
        
        # Çekilemeyen verileri status'e kaydet
        if result['unfetched_boards']:
            status['unfetched_boards'] = result['unfetched_boards']
        else:
            status.pop('unfetched_boards', None)
        
        self.save_status(status)
        
        return result
    
    def _compute_dd_for_hands(self):
        """Compute DD analysis for hands that don't have it"""
        try:
            from endplay.types import Deal, Player, Vul
            from endplay.dds import calc_dd_table
            
            with open(self.base_path / 'hands_database.json', 'r', encoding='utf-8') as f:
                hands_data = json.load(f)
            
            hands_without_dd = [h for h in hands_data if 'dd_analysis' not in h]
            
            if not hands_without_dd:
                logger.info("  ✓ Tüm ellerin DD analizi hazır")
                return
            
            logger.info(f"  {len(hands_without_dd)} el için DD hesaplanıyor...")
            
            updated = 0
            for hand in hands_without_dd:
                try:
                    # Get hand notation
                    north = hand.get('N', '')
                    south = hand.get('S', '')
                    east = hand.get('E', '')
                    west = hand.get('W', '')
                    
                    if not all([north, south, east, west]):
                        continue
                    
                    # Calculate dealer and vulnerability from board number
                    board_num = hand.get('board', 1)
                    dealer_idx = (board_num - 1) % 4
                    dealer = ['N', 'E', 'S', 'W'][dealer_idx]
                    
                    # Vulnerability: 16-board cycle
                    vul_cycle = ((board_num - 1) % 16)
                    if vul_cycle in [0, 1]:
                        vul = Vul.none
                    elif vul_cycle in [2, 3]:
                        vul = Vul.ns
                    elif vul_cycle in [4, 5]:
                        vul = Vul.ew
                    else:
                        vul = Vul.both
                    
                    # Create PBN string - endplay expects specific format
                    # Format: "N:north east south west" for North dealer
                    if dealer == 'N':
                        pbn = f"N:{north} {east} {south} {west}"
                    elif dealer == 'E':
                        pbn = f"E:{east} {south} {west} {north}"
                    elif dealer == 'S':
                        pbn = f"S:{south} {west} {north} {east}"
                    else:  # W
                        pbn = f"W:{west} {north} {east} {south}"
                    
                    # Parse and calculate
                    deal = Deal.from_pbn(pbn)
                    dd_table = calc_dd_table(deal, vul=vul)
                    
                    # Convert table to dict
                    dd_analysis = {}
                    for player in ['N', 'E', 'S', 'W']:
                        player_tricks = {}
                        for suit, tricks in [('C', dd_table[player].c), ('D', dd_table[player].d), 
                                           ('H', dd_table[player].h), ('S', dd_table[player].s), 
                                           ('NT', dd_table[player].nt)]:
                            player_tricks[suit] = int(tricks)
                        dd_analysis[player] = player_tricks
                    
                    hand['dd_analysis'] = dd_analysis
                    
                    # Calculate optimum contract
                    max_tricks = max(max(v.values()) for v in dd_analysis.values())
                    level = max_tricks - 6
                    if level > 0:
                        hand['optimum'] = {
                            'text': f'{"NS" if max_tricks >= 13 or (max_tricks == 12 and max(dd_analysis["N"].values()) >= 12) else "EW"} {level}NT; {20 + level*30}',
                            'score': 20 + level * 30,
                            'level': level
                        }
                    
                    updated += 1
                except Exception as e:
                    logger.debug(f"    DD hesaplama hatası board {hand.get('board')}: {e}")
                    continue
            
            # Save updated hands
            if updated > 0:
                with open(self.base_path / 'hands_database.json', 'w', encoding='utf-8') as f:
                    json.dump(hands_data, f, ensure_ascii=False, indent=2)
                logger.info(f"  ✓ {updated} el için DD hesaplandı")
        
        except ImportError:
            logger.warning("  ⚠️  endplay kütüphanesi yüklü değil - DD analizi atlanıyor")
            logger.warning("      Kurulum: pip install endplay")
        except Exception as e:
            logger.error(f"  ❌ DD hesaplama hatası: {e}")
    
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
            f"Toplam board çekildi: {status.get('total_boards_fetched', 0)}",
            f"Son hatalar: {len(status.get('errors', []))}",
        ]
        
        # Çekilemeyen verileri göster
        unfetched = status.get('unfetched_boards', {})
        if unfetched:
            total_unfetched = sum(len(boards) for boards in unfetched.values())
            lines.append(f"⚠️  Çekilemeyen board: {total_unfetched}")
        
        lines.append("=" * 50)
        
        return "\n".join(lines)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Scheduled Pipeline')
    parser.add_argument('--quick', action='store_true', help='Hızlı güncelleme')
    parser.add_argument('--full', action='store_true', help='Tam güncelleme')
    parser.add_argument('--rankings', action='store_true', help='Sadece board rankings generate et')
    parser.add_argument('--daemon', action='store_true', help='Daemon modu')
    parser.add_argument('--interval', type=int, default=30, help='Daemon aralığı (dakika)')
    parser.add_argument('--status', action='store_true', help='Durum göster')
    
    args = parser.parse_args()
    
    pipeline = ScheduledPipeline()
    
    if args.status:
        print(pipeline.get_status_summary())
        return
    
    if args.rankings:
        logger.info("Board rankings generate ediliyor...")
        try:
            from generate_board_rankings import BoardRankingsGenerator
            generator = BoardRankingsGenerator()
            if generator.generate_all():
                logger.info("✅ Board rankings başarılı şekilde generate edildi")
            else:
                logger.error("❌ Board rankings generate edilirken hata")
        except Exception as e:
            logger.error(f"❌ Board rankings hatası: {e}")
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
    print(f"\nSonuç: {'✅ BAŞARILI' if result['success'] else '❌ BAŞARISIZ'}")
    print(f"Çekilen hands: {result.get('hands_fetched', 0)}")
    print(f"Çekilen board: {result['boards_fetched']}")
    print(f"Düzeltilen event ID: {result['event_ids_fixed']}")
    if 'retry_attempts' in result:
        print(f"Retry denemesi: {result['retry_attempts']}")
    if result['unfetched_boards']:
        total_unfetched = sum(len(boards) for boards in result['unfetched_boards'].values())
        print(f"⚠️  Çekilemeyen board: {total_unfetched}")
    if result['errors']:
        print(f"Hatalar: {result['errors']}")


if __name__ == "__main__":
    main()
