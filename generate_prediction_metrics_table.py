import pandas as pd

df = pd.read_csv('prediction_metrics.csv').round({'rmse': 3, 'mae': 3, 'r2': 3})

fd = open('prediction_metrics_table.md', 'w')

fd.write('<font size="1">legend: $RMSE/MAE/R^2$</font>\n')

col_names = ['abs peakwavs max', 'emi peakwavs max', 'abs bandwidth', 'abs molar ext coeff', 'emi bandwidth', 'quantum yield', 'log lifetime']
col_names_full = ['maximum absorption wavelength', 'maximum emission wavelength', 'absorption bandwidth', 'absorption molar extinction coefficient', 'emission bandwidth', 'quantum yield', 'log lifetime']
split_types = ['group_by_smiles', 'random', 'scaffold']

opt_props = [i.replace(' ', '_') for i in col_names]

col_names_str = '| '
for i, c in enumerate(col_names_full):
    col_names_str += '| <font size="1">' + c + '</font> '
col_names_str += '|\n'
fd.write(col_names_str)

col_header = ''
for i in range(len(col_names) + 1):
    col_header += '| :---: '
col_header += '|\n'
fd.write(col_header)

for s in split_types:
    row = '| <font size="1">**' + s.replace('_', ' ') + '**</font> '
    for o in opt_props:
        cell = '<font size="1">'
        for index, col in df.iterrows():
            if col['property'] == o and col['split'] == s:
                combo_metrics = '**' + str(col['combo']) + ':** ' + str(col['rmse']) + '/' + str(col['mae']) + '/' + str(col['r2']) + ' '
                cell += combo_metrics
        row += '|' + cell + '</font> '
    row += '|\n'
    fd.write(row)

fd.close()