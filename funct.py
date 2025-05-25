import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
import matplotlib.pyplot as plt
from scipy.stats import shapiro, levene, kruskal, chisquare
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm


def qqplot(data, ax, color='blue'):
    """
    Tworzy wykres kwantyl-kwantyl z linią regresji i obszarem ufności.

    Parametry:
    - data: 1D array-like — dane wejściowe
    - ax: matplotlib.axes.Axes — oś, na której ma być narysowany wykres
    - color: str — kolor punktów i linii
    - x_label: str — etykieta osi X
    """
    # Posortowane dane i kwantyle teoretyczne
    sample = np.sort(np.asarray(data))
    n = len(sample)
    theoretical = stats.norm.ppf((np.arange(1, n + 1) - 0.5) / n)

    df = pd.DataFrame({'Theoretical': theoretical, 'Sample': sample})

    # Rysuj wykres z obszarem ufności
    sns.regplot(
        x='Theoretical',
        y='Sample',
        data=df,
        ax=ax,
        ci=95,
        scatter_kws={'color': color, 's': 40},
        line_kws={'color': color}
    )

    # Wyłącz domyślne etykiety osi
    ax.set_xlabel('')
    ax.set_ylabel('')

def export_data(df: pd.DataFrame, path):
    df.to_csv(path)
    pass

##################################################

def test_normalnosci(data, results):
    # Lista dostępnych transformacji z nazwami i funkcjami
    transformers = [
        ("pierwiastek kwadratowy", lambda x: np.sqrt(x)),
        ("pierwiastek czwartego stopnia", lambda x: np.power(x, 0.25)),
        ("log naturalny", lambda x: np.log(x)),
        ("log dziesiętny", lambda x: np.log10(x))
    ]
    
    data = pd.to_numeric(data, errors='coerce').dropna()
    
    if len(data) < 3:
        results.append("  Za mało danych do testu Shapiro-Wilka (min. 3 wartości).")
        return results, None

    try:
        stat, p = shapiro(data)
        normal = p > 0.05
        results.append(f"  Test Shapiro-Wilka: statystyka={stat:.4f}, p={p:.4f}")
        results.append(f"  TTFF normalny? {'TAK' if normal else 'NIE'}")
    except Exception as e:
        results.append(f"  Błąd w teście Shapiro-Wilka: {e}")
        return results, None

    # Jeśli dane nie są normalne, próbujemy transformacji
    if not normal:
        for name, func in transformers:
            try:
                # Sprawdź czy wszystkie wartości są dodatnie
                if any(data <= 0) and ('log' in name or 'pierwiastek' in name):
                    results.append(f"  Pominięto transformację ({name}): zawiera wartości <= 0.")
                    continue

                transformed = data.apply(func)
                stat2, p2 = shapiro(transformed.dropna())
                is_normal = p2 > 0.05
                results.append(f"  Próba transformacji: {name}")
                results.append(f"    statystyka={stat2:.4f}, p={p2:.4f}")
                results.append(f"    Czy normalne? {'TAK' if is_normal else 'NIE'}")
                
                if is_normal:
                    break  # nie kontynuuj dalszych transformacji jeśli się udało
            except Exception as e:
                results.append(f"  Błąd przy transformacji {name}: {e}")

    results.append("-" * 40)
    return results, normal


def statystyki_opisowe(series, results, name):
    # Konwersja do typu liczbowego
    series = pd.to_numeric(series, errors='coerce').dropna()

    # Obliczenia statystyczne
    mean_val = series.mean()
    std_val = series.std()
    median_val = series.median()
    min_val = series.min()
    max_val = series.max()
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)

    results.append(f"Plik: {name}")
    results.append(f"  Średnia: {mean_val:.4f}")
    results.append(f"  Odchylenie standardowe: {std_val:.4f}")
    results.append(f"  Mediana: {median_val:.4f}")
    results.append(f"  Min: {min_val:.4f}")
    results.append(f"  Max: {max_val:.4f}")
    results.append(f"  Kwartyl 1 (25%): {q1:.4f}")
    results.append(f"  Kwartyl 3 (75%): {q3:.4f}")
    return results


def test_rownolicznosci(data: list, results: list, file_label: str = ""):
    """
    Test chi-kwadrat na równoliczność liczby obserwacji w grupach.

    Parametry:
        data: list of pd.Series - lista serii danych pogrupowanych (np. TTFF dla każdej grupy)
        results: list - lista, do której będą dopisywane wyniki
        file_label: str - etykieta pliku/folderu do opisu
    """
    results.append(f"Test chi-kwadrat dla równoliczności obserwacji ({file_label}):")

    try:
        # Zlicz liczbę obserwacji w każdej grupie
        counts = [len(group) for group in data]
        num_groups = len(counts)

        # Ostrzeżenie jeśli nie są 3 grupy
        if num_groups != 3:
            results.append(f"  UWAGA: Oczekiwano 3 grup, znaleziono {num_groups}.")

        # Oczekiwane liczności
        expected = [np.mean(counts)] * num_groups

        # Test chi-kwadrat
        stat, p = chisquare(f_obs=counts, f_exp=expected)

        # Formatowanie słownika z nazwami grup
        group_counts = {f"Grupa {i+1}": count for i, count in enumerate(counts)}
        results.append(f"  Liczebności grup: {group_counts}")
        results.append(f"  Statystyka chi² = {stat:.4f}, p = {p:.4f}")

        # Wniosek
        if p < 0.05:
            results.append("  Odrzucamy H₀: liczba obserwacji w grupach nie jest równa.")
        else:
            results.append("  Brak podstaw do odrzucenia H₀: liczba obserwacji w grupach może być równa.")
    except Exception as e:
        results.append(f"  Błąd podczas testu chi-kwadrat: {e}")

    results.append("-" * 40)
    return results


def anova(data, results, normal, equal_var):
    if normal and equal_var:
        # ANOVA jednoczynnikowa
        try:
            df_anova = data.copy()
            df_anova['group'] = df_anova['group'].astype(str)
            model = ols('TTFF ~ C(group)', data=df_anova).fit()
            anova_results = anova_lm(model, typ=2)
            f_val = anova_results['F'].iloc[0]
            p_val = anova_results['PR(>F)'].iloc[0]
            results.append("  Wynik ANOVA:")
            results.append(f"    F = {f_val:.4f}, p = {p_val:.4f}")
        except Exception as e:
            results.append(f"  Błąd w obliczaniu ANOVA: {e}")
    else:
        # Test Kruskala-Wallisa
        try:
            stat_kw, p_kw = kruskal(*data)
            results.append("  Wynik testu Kruskala-Wallisa:")
            results.append(f"    statystyka={stat_kw:.4f}, p={p_kw:.4f}")
        except Exception as e:
            results.append(f"  Błąd w obliczaniu testu Kruskala-Wallisa: {e}")
    return results