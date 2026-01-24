import json

db = json.load(open('hands_database.json'))

# Check enrichment quality
print("="*60)
print("DATABASE ENRICHMENT CHECK")
print("="*60)

# Check first board
sample = db[0]
print(f"\nSample Board:")
print(f"  Board: {sample['board']}")
print(f"  Date: {sample['date']}")
print(f"  Has DD Analysis: {bool(sample.get('dd_analysis'))}")
print(f"  Has Optimum: {bool(sample.get('optimum'))}")
print(f"  Has LoTT: {bool(sample.get('lott'))}")

if sample.get('optimum'):
    print(f"  Optimum Score: {sample['optimum'].get('text')}")
if sample.get('lott'):
    print(f"  LoTT Total Tricks: {sample['lott'].get('total_tricks')}")

# Check all boards have enrichment
print(f"\nGlobal Coverage:")
with_dd = sum(1 for h in db if h.get('dd_analysis'))
with_optimum = sum(1 for h in db if h.get('optimum'))
with_lott = sum(1 for h in db if h.get('lott'))

print(f"  Total hands: {len(db)}")
print(f"  With DD Analysis: {with_dd} ({100*with_dd/len(db):.1f}%)")
print(f"  With Optimum: {with_optimum} ({100*with_optimum/len(db):.1f}%)")
print(f"  With LoTT: {with_lott} ({100*with_lott/len(db):.1f}%)")

# Find any missing enrichment
missing = []
for h in db:
    if not h.get('dd_analysis') or not h.get('optimum') or not h.get('lott'):
        missing.append((h['date'], h['board']))

if missing:
    print(f"\n⚠️  Missing enrichment in {len(missing)} boards:")
    for date, board in missing[:5]:
        print(f"    {date} - Board {board}")
else:
    print(f"\n✅ ALL BOARDS FULLY ENRICHED")

print("="*60)
