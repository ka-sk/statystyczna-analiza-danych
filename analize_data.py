import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import shapiro, levene, kruskal
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
import funct as fun

def analyze_base_folder(base_folder):
    # Analiza folderu *_base: statystyki opisowe i test Shapiro-Wilka dla plików T_*, R_*, Y_.
    base_folder = Path(base_folder)
    results = []

    all_data = []
    # Przetwarzaj pliki CSV rozpoczynające się od T_, R_ lub Y_
    for file_path in base_folder.glob("*.csv"):
        name = file_path.name
        if not (name.startswith("T_") or name.startswith("R_") or name.startswith("Y_")):
            continue
        # Wczytaj plik CSV
        try:
            df = pd.read_csv(file_path, header=None)
        except Exception as e:
            results.append(f"Nie można wczytać pliku {name}: {e}")
            continue
        # Sprawdź czy plik jest pusty
        if df.empty:
            results.append(f"Plik {name} jest pusty lub nie zawiera danych.")
            continue

        # Weź pierwszą kolumnę jako dane liczbowe, pomiń inne kolumny jeśli występują
        data = df.iloc[:, 0]
        data = pd.to_numeric(data, errors='coerce')  # konwersja do numeric, błędy na NaN
        data = data.dropna()
        if data.empty:
            results.append(f"Plik {name}: brak poprawnych danych liczbowych do analizy.")
            continue
        
        results.append(f"Plik: {name} w folderze {base_folder}")
        # Oblicz statystyki opisowe
        results = fun.statystyki_opisowe(data, results)
        # Test normalności Shapiro-Wilka
        results, normal = fun.test_normalnosci(data, results)

        if not data.empty:
            all_data.append(data)

    # Połącz wszystkie dane w jedną ramkę
    if not all_data:
        results.append(f"Brak poprawnych danych w folderze {base_folder.name}.")
        return

    # Sprawdź liczbę grup i wielkości próbek
    if len(all_data) < 2 or all(len(g) < 2 for g in all_data):
        results.append("  Brak wystarczających grup lub danych do testów porównawczych.")
    else:
        # Test Levene'a na równość wariancji
        try:
            stat_lev, p_lev = levene(*all_data)
            equal_var = (p_lev > 0.05)
            results.append(f"  Test Levene'a: statystyka={stat_lev:.4f}, p={p_lev:.4f}")
            results.append(f"  Wariancje równe? {'TAK' if equal_var else 'NIE'}")
        except Exception as e:
            results.append(f"  Błąd w teście Levene'a: {e}")
            equal_var = False

        # test równolicznosci chi kwadrat
        results = fun.test_rownolicznosci(all_data, results)

        # ANOVA lub Kruskal-Wallisa
        results = fun.anova(all_data, results, normal, equal_var)

    results.append("-" * 40)
    # Zapisz wyniki do pliku results.txt w folderze base
    output_file = base_folder / "results.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        for line in results:
            f.write(line + "\n")

def analyze_ttff_folder(ttff_folder):
    # Analiza folderu *_TTFF: statystyki TTFF, normalność, testy grupowe.
    ttff_folder = Path(ttff_folder)
    results = []
    all_data = []
    # Przetwarzaj pliki CSV w folderze TTFF
    for file_path in ttff_folder.glob("*.csv"):
        name = file_path.name
        # Wczytaj plik CSV
        try:
            df = pd.read_csv(file_path, header=None)
        except Exception as e:
            results.append(f"Nie można wczytać pliku {name}: {e}")
            continue

        # Sprawdź czy plik jest pusty
        if df.empty:
            results.append(f"Plik {name} jest pusty lub nie zawiera danych.")
            continue

        # Sprawdź liczbę kolumn (min. 4 wymagane)
        if df.shape[1] < 4:
            results.append(f"Plik {name}: zbyt mało kolumn (wymagane min. 4).")
            continue
        
        results.append(f"Plik: {name} w folderze {ttff_folder}")
        # Wybierz kolumnę 2 jako TTFF i kolumnę 3 jako zmienną grupującą
        TTFF = pd.to_numeric(df.iloc[:, 2], errors='coerce')
        group = df.iloc[:, 3]
        data = pd.DataFrame({'TTFF': TTFF, 'group': group})
        data = data.dropna(subset=['TTFF', 'group'])
        if data.empty:
            results.append(f"Plik {name}: brak poprawnych danych TTFF lub zmiennej grupującej.")
            continue

        # Statystyki opisowe TTFF
        results = fun.statystyki_opisowe(data['TTFF'], results)

        # Test normalności Shapiro-Wilka
        results, normal = fun.test_normalnosci(data['TTFF'], results)

        if not data.empty:
            all_data.append(data["TTFF"])

    # Połącz wszystkie dane w jedną ramkę
    if not all_data:
        results.append(f"Brak poprawnych danych w folderze {ttff_folder.name}.")
        return

    # Sprawdź liczbę grup i wielkości próbek
    if len(all_data) < 2 or all(len(g) < 2 for g in all_data):
        results.append("  Brak wystarczających grup lub danych do testów porównawczych.")
    else:
        # Test Levene'a na równość wariancji
        try:
            stat_lev, p_lev = levene(*all_data)
            equal_var = (p_lev > 0.05)
            results.append(f"  Test Levene'a: statystyka={stat_lev:.4f}, p={p_lev:.4f}")
            results.append(f"  Wariancje równe? {'TAK' if equal_var else 'NIE'}")
        except Exception as e:
            results.append(f"  Błąd w teście Levene'a: {e}")
            equal_var = False

        # test równolicznosci chi kwadrat
        results = fun.test_rownolicznosci(all_data, results)

        # ANOVA lub Kruskal-Wallisa
        results = fun.anova(all_data, results, normal, equal_var)

    results.append("-" * 40)

    # Zapisz wyniki do pliku results.txt w folderze TTFF
    output_file = ttff_folder / "results.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        for line in results:
            f.write(line + "\n")

def main():
    # Katalog główny z danymi
    data_dir = Path("data_to_analysis")
    if not data_dir.exists():
        print("Nie znaleziono katalogu 'data_to_analysis'.")
        return
    # Przeglądanie folderów zakończonych na _base
    for base_folder in data_dir.iterdir():
        print(f'Analiza folderów: {base_folder}')
        if base_folder.is_dir() and base_folder.name.endswith("_base"):
            analyze_base_folder(base_folder)
            # Szukaj odpowiadającego folderu TTFF
            prefix = base_folder.name[:-5]  # usuń sufiks '_base'
            ttff_folder = data_dir / f"{prefix}_TTFF"
            if ttff_folder.exists() and ttff_folder.is_dir():
                analyze_ttff_folder(ttff_folder)
            else:
                print(f"Nie znaleziono odpowiadającego folderu TTFF dla {base_folder.name}")

if __name__ == "__main__":
    main()


