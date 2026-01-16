import json

print("=== LOCAL DATABASE ===")
try:
    with open('database.json', 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    print(f"✅ Local: {len(data)} record")
    dates = sorted(set([r.get('Tarih') for r in data if r.get('Tarih')]), 
                   key=lambda x: tuple(map(int, x.split('.')[::-1])))
    print(f"📅 Son tarih: {dates[-1] if dates else 'N/A'}")
except Exception as e:
    print(f"❌ Hata: {e}")

print("\n=== GİT STATUS ===")
import subprocess
result = subprocess.run(['git', 'status', 'database.json'], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print(result.stderr)
