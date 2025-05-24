import pandas as pd
import os

# Ścieżka do pliku .ods
file_path = 'ALL_DATA_TRANSPARENT_YELLOW_RED GOGLES_ON_CONSTRUCTION_SITE.ods'

# Folder docelowy
output_folder = 'eksport_csv'
os.makedirs(output_folder, exist_ok=True)  # utwórz folder, jeśli nie istnieje

# Wczytanie wszystkich arkuszy
xls = pd.read_excel(file_path, sheet_name=None, engine='odf')

# Zapisz każdy arkusz jako osobny plik CSV
for sheet_name, df in xls.items():
    # Zamień niedozwolone znaki w nazwach plików
    safe_sheet_name = sheet_name.replace(" ", "_").replace("/", "_")
    output_path = os.path.join(output_folder, f"{safe_sheet_name}.csv")
    df.to_csv(output_path, index=False)
    print(f"Zapisano: {output_path}")
