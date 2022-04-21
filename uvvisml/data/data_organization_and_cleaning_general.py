# coding: utf-8

# # Imports

import pandas as pd
import os
import numpy as np
from rdkit.Chem import AllChem as Chem
import sys
sys.path.append('..')

#example args: true absPeak emiPeak
same_test_set = sys.argv[1] #either true or false
optical_properties = sys.argv[2:]

WORK_DIR = os.getcwd()
DATA_DIR = os.path.join(WORK_DIR,'original')

data_processed_dir = os.path.join(WORK_DIR,'processed')
if not os.path.exists(data_processed_dir):
    os.makedirs(data_processed_dir)


# # Read Raw Data

# Read the raw data files, rename columns, drop NaN and extraneous information

# ### Deep4Chem

data_location = os.path.join(DATA_DIR, 'joung/DB_for_chromophore_Sci_Data_rev02.csv')
joung_df = pd.read_csv(data_location)

# Drop columns that don't have data for specified optical properties
if same_test_set:
    prop_to_col = {'absPeak': 'Absorption max (nm)', 'emiPeak': 'Emission max (nm)', 'quantumYield': 'Quantum yield'}
    for p in optical_properties:
        empty_idx = joung_df[joung_df[prop_to_col[p]].isna()].index
        joung_df.drop(index=empty_idx, inplace=True)

# Rename columns
# columns = {'Chromophore':'smiles','Solvent':'solvent'}
# for property in optical_properties:
#     if property == 'absPeak':
#         columns['Absorption max (nm)'] = 'abs_peakwavs_max'
#     elif property == 'emiPeak':
#         columns['Emission max (nm)'] = 'emi_peakwavs_max'
#     elif property == 'absBand':
#         columns['abs FWHM (nm)'] = 'abs_bandwidth'
#     elif property == 'emiBand':
#         columns['emi FWHM (nm)'] = 'emi_bandwidth'
#     elif property == 'quantumYield':
#         columns['Quantum yield'] = 'quantum_yield'
#     elif property == 'logLife':
#         columns['Lifetime (ns)'] = 'log_lifetime'
#     elif property == 'absMol':
#         columns['log(e/mol-1 dm3 cm-1)'] = 'abs_molar_ext_coeff'
columns = {'Chromophore':'smiles','Solvent':'solvent', 'Absorption max (nm)':'abs_peakwavs_max', 
           'Emission max (nm)':'emi_peakwavs_max', 'abs FWHM (nm)':'abs_bandwidth',
           'emi FWHM (nm)':'emi_bandwidth', 'Quantum yield':'quantum_yield', 'Lifetime (ns)':'log_lifetime',
           'log(e/mol-1 dm3 cm-1)':'abs_molar_ext_coeff'}

joung_df.rename(columns=columns, 
                inplace=True)

# Drop columns of all other properties if creating same test set
if same_test_set:
    all_columns = list(joung_df.columns)
    dropped_columns = all_columns.copy()
    kept_columns = ['smiles', 'solvent']
    for c in all_columns[2:]: #excluding 'smiles' and 'solvent' columns
        for p in optical_properties:
            if c != columns[prop_to_col[p]]:
                continue
            else:
                dropped_columns.remove(c)
                kept_columns.append(c)
    dropped_columns = dropped_columns[3:] #excluding 'Tag', smiles', and 'solvent' columns
    joung_df.drop(axis=1, labels=dropped_columns, inplace=True)

# Drop measurements where solvent == 'gas'
gas_idx = joung_df[joung_df['solvent']=='gas'].index
joung_df.drop(index=gas_idx, inplace=True)

# Drop measurements taken in solid state (original authors wrote file as chromophore == solvent for these cases)
ss_idx = joung_df[joung_df['smiles']==joung_df['solvent']].index
joung_df.drop(index=ss_idx, inplace=True)

# Create df with target properties and drop NaNs
if same_test_set:
    col_names = kept_columns
else:
    col_names = list(columns.values())
joung_df = joung_df[col_names].copy()
joung_df.dropna(inplace=True)
joung_df['source'] = 'deep4chem'

df = joung_df
prop_col_names = col_names[2:]
for col_name in prop_col_names:
    df = df.loc[df[col_name]!='-'].copy()
    df[col_name] = df[col_name].apply(lambda x: float(x))


# # Filtering

# ### Remove Molecules that Cannot be Sanitized by RDKit

def sanitize_smiles(smiles):
    try:
        smiles = Chem.MolToSmiles(Chem.MolFromSmiles(smiles))
    except:
        smiles = np.nan
    return smiles

df['smiles'] = df['smiles'].apply(lambda x: sanitize_smiles(x))
df['solvent'] = df['solvent'].apply(lambda x: sanitize_smiles(x))
df.dropna(inplace=True)


# ### Remove Clusters (SMILES containing ".")

cluster_idx = df[df['smiles'].str.contains('\.')].index
#print('Removing {} rows'.format(len(cluster_idx)))
df.drop(index=cluster_idx, inplace=True)


# # Export DataFrame to CSV File

if same_test_set:
    file_name = 'data_same_test_set_'
else:
    file_name = ''
for i, property in enumerate(optical_properties):
    file_name += property
    if len(optical_properties) > 1 and i < (len(optical_properties) - 1):
        file_name += '_'
file_name += '.csv'

x = col_names + ['source']
df[x].to_csv(f'{data_processed_dir}/{file_name}', 
                                                        index=False)

x_1 = x.copy()
x_1 = x_1[:3] + x_1[3+1 :]
file_name_1 = 'data_same_test_set_absPeak.csv'
df[x_1].to_csv(f'{data_processed_dir}/{file_name_1}', 
                                                        index=False)

x_2 = x.copy()
x_2 = x_2[:2] + x_2[2+1 :]
file_name_2 = 'data_same_test_set_emiPeak.csv'
df[x_2].to_csv(f'{data_processed_dir}/{file_name_2}', 
                                                        index=False)


# # Stats

# ### Table 2

df.drop_duplicates(subset=['smiles','solvent'])

df.groupby(['smiles','solvent']).count().query('source > 1')


# ### Table S1

dict(df['solvent'].value_counts())