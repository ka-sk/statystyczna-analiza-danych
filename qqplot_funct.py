import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
import matplotlib.pyplot as plt

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