#!/usr/bin/env python3
"""
Event Registry - Single Source of Truth for Event IDs

Bu modül, tüm JSON dosyaları arasında event ID tutarlılığını sağlar.
database.json'daki legacy_records linklerinden event ID çıkarır ve
diğer tüm dosyalar bu registry'yi kullanır.

Kullanım:
    from event_registry import EventRegistry
    
    registry = EventRegistry()
    event_id = registry.get_event_id("14.01.2026")  # Returns "405007"
    date = registry.get_date("405007")  # Returns "14.01.2026"
"""

import json
import re
from pathlib import Path
from typing import Optional, Dict, List, Set
from datetime import datetime


class EventRegistry:
    """
    Event ID ve Tarih mapping'ini yöneten singleton-like sınıf.
    Tüm veri kaynaklarından tutarlı event ID'ler sağlar.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if EventRegistry._initialized:
            return
        
        self.base_path = Path(__file__).parent
        self.database_file = self.base_path / "database.json"
        self.hands_file = self.base_path / "hands_database.json"
        self.board_results_file = self.base_path / "board_results.json"
        
        # Mapping'ler
        self._date_to_event: Dict[str, str] = {}
        self._event_to_date: Dict[str, str] = {}
        self._event_to_name: Dict[str, str] = {}
        
        # Load registry
        self._load_registry()
        EventRegistry._initialized = True
    
    def _load_registry(self):
        """database.json'dan event mapping'lerini yükle"""
        try:
            with open(self.database_file, 'r', encoding='utf-8') as f:
                db = json.load(f)
        except Exception as e:
            print(f"[EventRegistry] database.json okunamadı: {e}")
            return
        
        # 1. events section'dan al (yeni format)
        for event_key, event_data in db.get('events', {}).items():
            date = event_data.get('date')
            event_id = event_data.get('id')
            name = event_data.get('name', '')
            if date and event_id:
                self._date_to_event[date] = event_id
                self._event_to_date[event_id] = date
                self._event_to_name[event_id] = name
        
        # 2. legacy_records'tan al (eski format, Link'ten event ID çıkar)
        for record in db.get('legacy_records', []):
            date = record.get('Tarih')
            link = record.get('Link', '')
            name = record.get('Turnuva', '')
            
            match = re.search(r'event=(\d+)', link)
            if match and date:
                event_id = match.group(1)
                # Sadece yoksa ekle (events section öncelikli)
                if date not in self._date_to_event:
                    self._date_to_event[date] = event_id
                if event_id not in self._event_to_date:
                    self._event_to_date[event_id] = date
                if event_id not in self._event_to_name:
                    self._event_to_name[event_id] = name
        
        print(f"[EventRegistry] {len(self._date_to_event)} tarih, {len(self._event_to_date)} event yüklendi")
    
    def reload(self):
        """Registry'yi yeniden yükle"""
        self._date_to_event.clear()
        self._event_to_date.clear()
        self._event_to_name.clear()
        self._load_registry()
    
    def get_event_id(self, date: str) -> Optional[str]:
        """
        Tarihten event ID al
        
        Args:
            date: "DD.MM.YYYY" formatında tarih
            
        Returns:
            Event ID string veya None
        """
        return self._date_to_event.get(date)
    
    def get_date(self, event_id: str) -> Optional[str]:
        """
        Event ID'den tarih al
        
        Args:
            event_id: Event ID string
            
        Returns:
            "DD.MM.YYYY" formatında tarih veya None
        """
        return self._event_to_date.get(str(event_id))
    
    def get_event_name(self, event_id: str) -> str:
        """Event ID'den turnuva adını al"""
        return self._event_to_name.get(str(event_id), "")
    
    def get_all_events(self) -> Dict[str, str]:
        """Tüm date -> event_id mapping'ini döndür"""
        return self._date_to_event.copy()
    
    def get_all_dates(self) -> List[str]:
        """Tüm tarihleri sıralı döndür"""
        return sorted(self._date_to_event.keys(), 
                     key=lambda x: datetime.strptime(x, "%d.%m.%Y"))
    
    def get_recent_events(self, days: int = 30) -> Dict[str, str]:
        """Son N günün event'lerini döndür"""
        today = datetime.now()
        result = {}
        
        for date_str, event_id in self._date_to_event.items():
            try:
                date = datetime.strptime(date_str, "%d.%m.%Y")
                if (today - date).days <= days:
                    result[date_str] = event_id
            except:
                continue
        
        return result
    
    def validate_hands_database(self) -> List[dict]:
        """
        hands_database.json'daki event ID'leri doğrula
        
        Returns:
            Tutarsız kayıtların listesi
        """
        issues = []
        
        try:
            with open(self.hands_file, 'r', encoding='utf-8') as f:
                hands = json.load(f)
        except Exception as e:
            return [{"error": f"hands_database.json okunamadı: {e}"}]
        
        for i, hand in enumerate(hands):
            date = hand.get('Tarih')
            event_id = str(hand.get('event_id'))
            
            expected_event = self.get_event_id(date)
            if expected_event and expected_event != event_id:
                issues.append({
                    "index": i,
                    "date": date,
                    "current_event_id": event_id,
                    "expected_event_id": expected_event
                })
        
        return issues
    
    def fix_hands_database(self, dry_run: bool = True) -> int:
        """
        hands_database.json'daki event ID'leri düzelt
        
        Args:
            dry_run: True ise sadece kontrol yapar, False ise düzeltir
            
        Returns:
            Düzeltilen kayıt sayısı
        """
        issues = self.validate_hands_database()
        
        if not issues or dry_run:
            return len(issues)
        
        try:
            with open(self.hands_file, 'r', encoding='utf-8') as f:
                hands = json.load(f)
            
            for issue in issues:
                hands[issue['index']]['event_id'] = issue['expected_event_id']
            
            with open(self.hands_file, 'w', encoding='utf-8') as f:
                json.dump(hands, f, ensure_ascii=False, indent=2)
            
            return len(issues)
        except Exception as e:
            print(f"[EventRegistry] hands_database düzeltilemedi: {e}")
            return 0
    
    def validate_board_results(self) -> List[str]:
        """
        board_results.json'daki event ID'leri doğrula
        
        Returns:
            Eksik event ID'lerin listesi
        """
        try:
            with open(self.hands_file, 'r', encoding='utf-8') as f:
                hands = json.load(f)
            with open(self.board_results_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
        except Exception as e:
            return [f"Dosya okunamadı: {e}"]
        
        # hands_database'deki tüm event'ler
        hands_events = set(str(h.get('event_id')) for h in hands)
        
        # board_results'taki event'ler
        results_events = set(k.split('_')[0] for k in results.get('boards', {}).keys())
        
        # Eksikler
        missing = sorted(hands_events - results_events)
        return missing
    
    def get_missing_boards_count(self) -> Dict[str, int]:
        """
        Her event için eksik board sayısını döndür
        
        Returns:
            {event_id: eksik_board_sayısı} dict
        """
        try:
            with open(self.hands_file, 'r', encoding='utf-8') as f:
                hands = json.load(f)
            with open(self.board_results_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
        except Exception as e:
            return {}
        
        # hands_database'den event -> board listesi
        hands_boards = {}
        for h in hands:
            event_id = str(h.get('event_id'))
            board = h.get('Board')
            if event_id not in hands_boards:
                hands_boards[event_id] = set()
            hands_boards[event_id].add(board)
        
        # board_results'tan mevcut boardlar
        results_boards = {}
        for key in results.get('boards', {}).keys():
            parts = key.split('_')
            if len(parts) == 2:
                event_id, board = parts
                if event_id not in results_boards:
                    results_boards[event_id] = set()
                results_boards[event_id].add(int(board))
        
        # Eksikleri hesapla
        missing = {}
        for event_id, boards in hands_boards.items():
            existing = results_boards.get(event_id, set())
            missing_boards = boards - existing
            if missing_boards:
                missing[event_id] = len(missing_boards)
        
        return missing


# Convenience functions
_registry = None

def get_registry() -> EventRegistry:
    """Global registry instance'ını al"""
    global _registry
    if _registry is None:
        _registry = EventRegistry()
    return _registry


def get_event_id(date: str) -> Optional[str]:
    """Tarihten event ID al"""
    return get_registry().get_event_id(date)


def get_date(event_id: str) -> Optional[str]:
    """Event ID'den tarih al"""
    return get_registry().get_date(event_id)


def validate_all() -> dict:
    """Tüm veritabanlarını doğrula"""
    registry = get_registry()
    return {
        "hands_issues": registry.validate_hands_database(),
        "missing_board_results": registry.validate_board_results(),
        "missing_boards_count": registry.get_missing_boards_count()
    }


if __name__ == "__main__":
    # Test
    registry = EventRegistry()
    
    print("\n=== Event Registry Test ===")
    
    # Örnek sorgular
    test_date = "14.01.2026"
    event_id = registry.get_event_id(test_date)
    print(f"\n{test_date} -> Event ID: {event_id}")
    
    if event_id:
        date_back = registry.get_date(event_id)
        print(f"Event {event_id} -> Tarih: {date_back}")
        print(f"Turnuva: {registry.get_event_name(event_id)}")
    
    # Doğrulama
    print("\n=== Doğrulama ===")
    
    hands_issues = registry.validate_hands_database()
    print(f"hands_database tutarsızlık: {len(hands_issues)}")
    
    missing_br = registry.validate_board_results()
    print(f"board_results eksik event: {len(missing_br)}")
    
    missing_boards = registry.get_missing_boards_count()
    print(f"Eksik board olan event: {len(missing_boards)}")
    if missing_boards:
        for eid, count in list(missing_boards.items())[:5]:
            print(f"  Event {eid}: {count} board eksik")
    
    # Son 7 günün event'leri
    print("\n=== Son 7 Günün Event'leri ===")
    recent = registry.get_recent_events(7)
    for date, eid in sorted(recent.items()):
        name = registry.get_event_name(eid)
        print(f"  {date}: {eid} - {name[:50]}...")
