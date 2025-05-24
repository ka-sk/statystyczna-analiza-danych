import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from pathlib import Path
from pandas.api.types import is_numeric_dtype
import qqplot_funct as qq

# Styl wykresów
sns.set(style="whitegrid")

prefixes = ['T_', 'R_', 'Y_']
suffixes = ['SEX', 'EXPERIENCE', 'H&STEST_RESULTS', 'TIME', 'AGE', 'TTFF']
file_format = '.csv' 
data_path = 'eksport_csv'
plot_path = Path('plots')

colors = ['#4F6D7A', '#AE4A4A', '#DE9543']
col_names = ['sex', 'Experience', 'TEST 0-10 points', 'T task [s]', 'AGE', 'R jacket']
x_labels = ['Gogle transparentne', 'Gogle czerwone', "Gogle żółte"]
titles = ['Płeć badanych', "Doświadczenie zawodowe badanych", 'Wyniki testu BHP wśród badanych', 'Czas noszenia gogli przez badanych', "Wiek badanych", 'Wykres kwantyl-kwantyl']

for file_idx, suf in enumerate(suffixes):
    # Sprawdzenie czy generować qqplot i boxplot
    if_qqplot = suf == "TTFF"
    
    # stworzenie obrazka z histagramem
    hist_fig, hist_ax = plt.subplots(nrows=1, ncols=3, figsize=[8, 5])

    # stworzenie obrazka z boxplotami
    box_fig, box_ax = plt.subplots(nrows=1, ncols=3, figsize=[8, 2])

    # stworzenie obrazka qqplot
    qq_fig, qq_ax = plt.subplots(nrows=1, ncols=3, figsize=[8, 5])

    # Tworzenie subplotów dla każdego koloru gogli w tej kategorii
    for col_idx, pre in enumerate(prefixes):
        # wczytanie danych
        file_name = Path(pre + suf + file_format)
        file_name = Path(data_path) / file_name
        data = pd.read_csv(file_name, header=1)

        #sprawdzenie czy rysowanie i zapis boxplotu się odbędzie
        if_boxplot = is_numeric_dtype(data[col_names[file_idx]])

        # rysowanie histogramu
        hist_ax[col_idx].hist(data[col_names[file_idx]], color=colors[col_idx])
        hist_ax[col_idx].set_xlabel(x_labels[col_idx])

        # rysowanie boxplotów
        if if_boxplot:
            box_ax[col_idx].boxplot(data[col_names[file_idx]], 
                                    orientation='horizontal', 
                                    patch_artist=True,
                                    boxprops=dict(facecolor=colors[col_idx]),
                                    widths=0.5)
        # rysowanie qqplotów
        if if_qqplot:
            qq.qqplot(data[col_names[file_idx]], box_ax[col_idx], colors[col_idx])
            box_fig.supxlabel('Dane teoretyczne')
            box_fig.supylabel('Dane doświadczalne')
            pass

    hist_fig.supylabel("Liczba wystąpień")
    hist_fig.suptitle(titles[file_idx])   
    hist_fig.savefig(plot_path / f'{suf}_hist.eps')
    hist_fig.savefig(plot_path / f'{suf}_hist.png')
    plt.close(hist_fig)

    if if_boxplot:
        box_fig.savefig(plot_path / f'{suf}_box.eps')
        box_fig.savefig(plot_path / f'{suf}_box.png')
        plt.close(box_fig)

    if if_qqplot:
        qq_fig.savefig(plot_path / f'{suf}_qq.eps')
        qq_fig.savefig(plot_path / f'{suf}_qq.png')
        plt.close(qq_fig)
    
    pass

'''#####################################
#### 1. Rozkład wieku

#### 2. Rozkład płci

#### 3. Test BHP

#### 4. Doświadczenie

#####################################
#### 5. Czas noszenia gogli

# 6. Testy statystyczne — porównanie czasów między grupami

#####################################
# 7. Wpływ testu BHP na TTFF

# 8. Wpływ płci na TTFF

# 9. Wpływ doświadczenia

# 10. Wpływ wieku

#####################################
# 11. Rozkład TTFF dla czerwonej kurtki

# 12. QQ-plot (kwantyl-kwantyl)

# 13. Testy normalności
print("Test Shapiro TTFF (czerwona):", stats.shapiro(red_ttff.dropna()))
'''
