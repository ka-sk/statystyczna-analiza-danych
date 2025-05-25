import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
import matplotlib.pyplot as plt
from scipy.stats import shapiro, levene, kruskal

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