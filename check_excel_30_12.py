import pandas as pd

# Load from Excel (hosgoru.py saved to xlsx)
df = pd.read_excel('database.xlsx')

# Check for 30.12.2025
records_30_12 = df[df['Tarih'] == '30.12.2025']

print(f"Database.xlsx içinde 30.12.2025: {len(records_30_12)} kayıt")

if len(records_30_12) > 0:
    print("\nİlk 3 kayıt:")
    for idx, (_, r) in enumerate(records_30_12.head(3).iterrows(), 1):
        print(f"{idx}. {r.get('Turnuva', '')} - {r.get('Oyuncu 1', '')} - {r.get('Skor', '')}")
else:
    # Check what dates DO have records with "Salı"
    print("\nTurnuva adında 'Salı' olan kayıtlar:")
    sali_records = df[df['Turnuva'].str.contains('Salı', na=False, case=False)]
    print(f"Toplam: {len(sali_records)}")
    if len(sali_records) > 0:
        print("Tarihler:", sali_records['Tarih'].unique()[:10])
