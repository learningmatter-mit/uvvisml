# coding: utf-8

# # Imports

import pandas as pd
import os
import numpy as np
from rdkit.Chem import AllChem as Chem
import sys
sys.path.append('..')

optical_properties = sys.argv[1:]

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

# Rename columns
columns = {'Chromophore':'smiles','Solvent':'solvent'}
for property in optical_properties:
    if property == 'absPeak':
        columns['Absorption max (nm)'] = 'abs_peakwavs_max'
    elif property == 'emiPeak':
        columns['Emission max (nm)'] = 'emi_peakwavs_max'
    elif property == 'absBand':
        columns['abs FWHM (nm)'] = 'abs_bandwidth'
    elif property == 'emiBand':
        columns['emi FWHM (nm)'] = 'emi_bandwidth'
    elif property == 'quantumYield':
        columns['Quantum yield'] = 'quantum_yield'
    elif property == 'logLife':
        columns['Lifetime (ns)'] = 'log_lifetime'
    elif property == 'absMol':
        columns['log(e/mol-1 dm3 cm-1)'] = 'abs_molar_ext_coeff'

joung_df.rename(columns=columns, 
                inplace=True)

# Drop measurements where solvent == 'gas'
gas_idx = joung_df[joung_df['solvent']=='gas'].index
joung_df.drop(index=gas_idx, inplace=True)

# Drop measurements taken in solid state (original authors wrote file as chromophore == solvent for these cases)
ss_idx = joung_df[joung_df['smiles']==joung_df['solvent']].index
joung_df.drop(index=ss_idx, inplace=True)

# Create df with target properties and drop NaNs
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

file_name = ''
for i, property in enumerate(optical_properties):
    file_name += property
    if len(optical_properties) > 1 and i < (len(optical_properties) - 1):
        file_name += '_'
file_name += '.csv'

x = col_names + ['source']
df[x].to_csv(f'{data_processed_dir}/{file_name}', 
                                                        index=False)

# # Stats

# ### Table 2

df.drop_duplicates(subset=['smiles','solvent'])

df.groupby(['smiles','solvent']).count().query('source > 1')


# ### Table S1

dict(df['solvent'].value_counts())