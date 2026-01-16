import json

# Kontrol: Tüm gerekli element IDs var mı?
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

required_ids = [
    'mobileResultsModal',
    'dailyResultsContent',
    'currentPage',
    'modalHeaderLabel',
    'dailyPrevBtn',
    'dailyNextBtn',
    'globalStatsModal',
    'globalModalContent',
    'globalNavFooter'
]

print("📋 Element ID Kontrolü:")
missing = []
for elem_id in required_ids:
    if f'id="{elem_id}"' in html:
        print(f"  ✓ {elem_id}")
    else:
        print(f"  ✗ {elem_id} BULUNAMADI!")
        missing.append(elem_id)

if missing:
    print(f"\n❌ Eksik elementler: {missing}")
else:
    print("\n✅ Tüm gerekli elementler var!")
