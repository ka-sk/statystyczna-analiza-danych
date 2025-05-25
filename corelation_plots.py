import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from matplotlib.ticker import MaxNLocator
import funct as f
import os

# Styl wykresów
sns.set(style="whitegrid")

prefixes = ['T_', 'R_', 'Y_']
suffixes = ['SEX', 'EXPERIENCE', 'H&STEST_RESULTS', 'TIME', 'AGE']
file_format = '.csv' 
data_path = 'eksport_csv'
plot_path = Path('corelation_plots')

colors = ["#310906",
          "#3e5168",
          "#90605e",
          "#8fb7b0",
          "#633533",
          "#597380",
          "#222e50"]

col_names = ['sex', 'Experience', 'TEST 0-10 points', 'T task [s]', 'AGE']
subtitels = ['Histogram TTFF z podziałem na płeć', 
             'Histogram TTFF z podziałem na doświadczenie zawodowe', 
             'Histogram TTFF z podziałem na wynik testu BHP 0-10', 
             'Histogram TTFF z podziałem na czas noszenia gogli',
             'Histogram TTFF z podziałem na wiek']

id_column = 'participant nr'

plot_blacklist = {'SEX': ['O'], 
                  'H&STEST_RESULTS': [7]}

save_data_path = Path('data_to_analysis')

TTFF_df = [0]*3
# wczytanie TTFF
for idx, pre in enumerate(prefixes):
    file_name = Path(pre + 'TTFF' + file_format)
    file_name = Path(data_path) / file_name
    TTFF_df[idx] = pd.read_csv(file_name, header=1)
    TTFF_df[idx] = TTFF_df[idx][[id_column, 'R jacket']]

TTFF_df = pd.concat(TTFF_df)

# wczytanie danych do analizy
for file_idx, category in enumerate(suffixes):

    cat_df = [0]*3
    for idx, pre in enumerate(prefixes):
        # wczytanie odpowiedniej kategorii danych
        file_name = Path(pre + category + file_format)
        file_name = Path(data_path) / file_name
        cat_df[idx] = pd.read_csv(file_name, header=1)
        cat_df[idx] = cat_df[idx][[id_column, col_names[file_idx]]]
    cat_df = pd.concat(cat_df)

    # łączenie df w jeden wspólny na podstawie participant nr
    merged_df = pd.merge(TTFF_df, cat_df, on=id_column)

    # zwolnienie pamięci
    del cat_df

    # stworzenie listy subplotów
    sb_names = list(set(merged_df[col_names[file_idx]]))

    # filtrowanie błędnych wykresów
    if category in plot_blacklist.keys():
        sb_names = [i for i in sb_names if i not in plot_blacklist[category]]

    if_grouped=False
    # grupowanie w przypadku zbyt wielu etykiet
    if len(sb_names) > 3:
        n = len(sb_names)//3 + 1
        sb_names = [sb_names[i:i + n] for i in range(0, len(sb_names), n)]

        if_grouped=True

    # stworzenie subplotów
    hist_fig, hist_ax = plt.subplots(nrows=1, ncols=len(sb_names))

    for idx, ax in enumerate(hist_ax):

        # tworzenie wykresu
        if not if_grouped:
            #filtracja danych
            plot_data = merged_df[merged_df[col_names[file_idx]] == sb_names[idx]]   

            # wykres
            ax.hist(plot_data['R jacket'], color=colors[idx])
            temp_name = str(sb_names[idx])

        else:
            # filtracja dla pogrupowanych danych
            plot_data = merged_df[merged_df[col_names[file_idx]].isin(sb_names[idx])]

            # wykres
            ax.hist(plot_data['R jacket'], color=colors[idx])

            if category == 'AGE':
                temp_name = f'{sb_names[idx][0]} - {sb_names[idx][-1]} [y]'
            elif category == 'TIME':
                temp_name = f'{sb_names[idx][0]} - {sb_names[idx][-1]} [s]'
            else: 
                temp_name = f'{sb_names[idx][0]} - {sb_names[idx][-1]}'

        ax.set_title(temp_name)
        # ustal, by oś Y miała tylko liczby całkowite
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        # eksport danych
        dir_name = category + '_TTFF'
        os.makedirs(save_data_path / dir_name, exist_ok=True)
        f.export_data(plot_data,save_data_path / Path(dir_name) / Path(temp_name + '.csv'))

    hist_fig.suptitle(subtitels[file_idx])
    hist_fig.supxlabel("Czas do pierwszej fiksacji [s]")
    hist_fig.supylabel("Liczba wystapień")
    hist_fig.savefig(plot_path / f'{category}_hist.eps')
    hist_fig.savefig(plot_path / f'{category}_hist.png')
    #plt.show()
    plt.close(hist_fig)
    pass
'''
#####################################
#### 5. Czas noszenia gogli

# 6. Testy statystyczne — porównanie czasów między grupami

#####################################
#### 7. Wpływ testu BHP na TTFF

#### 8. Wpływ płci na TTFF

#### 9. Wpływ doświadczenia

#### 10. Wpływ wieku

#####################################
#### 11. Rozkład TTFF dla czerwonej kurtki

#### 12. QQ-plot (kwantyl-kwantyl)

# 13. Testy normalności
print("Test Shapiro TTFF (czerwona):", stats.shapiro(red_ttff.dropna()))
'''