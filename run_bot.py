#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import time
import os
import argparse

def run_bot_with_retry(max_retries=5, lang='tr'):
    """Bot'u çalıştır, başarısız olursa tekrar dene / Run bot with retries"""
    texts = {
        'tr': {
            'attempt': 'DENEME {current}/{total}',
            'success': '✓ Bot başarıyla tamamlandı!',
            'rc_error': '✗ Bot hata ile çıktı (return code: {rc})',
            'timeout': '✗ Bot timeout\'a çıktı (30 dakika aşıldı)',
            'stopped': '✗ Bot durduruldu',
            'error': '✗ Hata: {err}',
            'retry_wait': '⏳ {sec} saniye sonra tekrar deneyelim...',
            'failed': '❌ Bot tüm denemelerden sonra başarısız oldu'
        },
        'en': {
            'attempt': 'ATTEMPT {current}/{total}',
            'success': '✓ Bot completed successfully!',
            'rc_error': '✗ Bot exited with error (return code: {rc})',
            'timeout': '✗ Bot timed out (30 minutes exceeded)',
            'stopped': '✗ Bot stopped',
            'error': '✗ Error: {err}',
            'retry_wait': '⏳ Retrying in {sec} seconds...',
            'failed': '❌ Bot failed after all attempts'
        }
    }
    t = texts['tr' if lang not in ('tr','en') else lang]
    
    for attempt in range(1, max_retries + 1):
        print(f"\n{'='*60}")
        print(t['attempt'].format(current=attempt, total=max_retries))
        print(f"{'='*60}\n")
        
        try:
            env = os.environ.copy()
            env['HOSGORU_LANG'] = lang
            result = subprocess.run(
                ['python', 'hosgoru_takvim_bot.py'],
                cwd=r'c:\Users\metin\Desktop\BRİÇ',
                capture_output=False,
                text=True,
                timeout=1800,  # 30 dakika timeout / 30-min timeout
                env=env
            )
            
            if result.returncode == 0:
                print("\n" + t['success'])
                return True
            else:
                print("\n" + t['rc_error'].format(rc=result.returncode))
                
        except subprocess.TimeoutExpired:
            print("\n" + t['timeout'])
        except KeyboardInterrupt:
            print("\n" + t['stopped'])
            break
        except Exception as e:
            print("\n" + t['error'].format(err=e))
        
        if attempt < max_retries:
            wait_time = 5 * attempt  # Artan bekleme süresi / increasing backoff
            print("\n" + t['retry_wait'].format(sec=wait_time))
            time.sleep(wait_time)
    
    print(f"\n{'='*60}")
    print(t['failed'])
    print(f"{'='*60}")
    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run Hoşgörü bot with retries')
    parser.add_argument('--lang', choices=['tr','en'], default='tr', help='Output language (tr or en)')
    parser.add_argument('--retries', type=int, default=3, help='Max retry attempts')
    args = parser.parse_args()

    success = run_bot_with_retry(max_retries=args.retries, lang=args.lang)
    exit(0 if success else 1)
