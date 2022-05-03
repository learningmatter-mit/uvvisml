from os import listdir
from os.path import isfile, join

mypath = "./prediction_plots_images"
onlyfiles = sorted([f for f in listdir(mypath) if isfile(join(mypath, f))])

fd = open('prediction_plots_table.md', 'w')

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
    col_header += '| --- '
col_header += '|\n'
fd.write(col_header)

for s in split_types:
    row = '| <font size="1">**' + s.replace('_', ' ') + '**</font> '
    for o in opt_props:
        cell = ''
        for f in onlyfiles:
            if s in f and o in f:
                # cell += ' ' + '![](./prediction_plots_images/' + f + ')'
                cell += '<img src="./prediction_plots_images/' + f + '" width="50">'
        row += '|' + cell + ' '
    row += '|\n'
    fd.write(row)

fd.close()