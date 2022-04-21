import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import StandardScaler
from scaffold_splits import scaffold_split
import sys

optical_properties = sys.argv[1:]

target_names = []
for property in optical_properties:
    if property == 'absPeak':
        target_names.append('abs_peakwavs_max')
    elif property == 'emiPeak':
        target_names.append('emi_peakwavs_max')
    elif property == 'absBand':
        target_names.append('abs_bandwidth')
    elif property == 'emiBand':
        target_names.append('emi_bandwidth')
    elif property == 'quantumYield':
        target_names.append('quantum_yield')
    elif property == 'logLife':
        target_names.append('log_lifetime')
    elif property == 'absMol':
        target_names.append('abs_molar_ext_coeff')

def data_split_and_write(X, feature_names=None, target_names=target_names, solvation=False, split_type='scaffold',
                         scale_targets=False, write_files=False, random_seed=0):
    """Writes train, val, test CSV files for Chemprop with a given dataset.

    Parameters
    ----------
    X : pandas DataFrame
        DataFrame to be split (has columns: 'smiles', target_names, and feature_names
        (and 'solvent' if solvation=True))
    feature_names : list of str or None
        Names of feature columns in X to be added to feature files (default is None)
    target_names : list of str
        Names of target columns to be printed to files (default is ['peakwavs_max'])
    solvation : bool
        Specify whether to include solvents in target file (default is False)
    split_type : str
        which type of splitting to use ('scaffold', 'group_by_smiles', or 'random')
    scale_targets : bool
        whether to scale targets to have mean 0 and standard deviation 1 (default is False)
    write_files : bool
        whether to write the resulting splits to files
    random_seed : int or None
        number to provide for the seed / random_state arguments to make splits reproducible
        (use None if doing multiple splits for cross validation)

    """

    if split_type=='scaffold':
        X_train, X_val, X_test = scaffold_split(X, sizes=(0.8, 0.1, 0.1), balanced=True, seed=random_seed)
    elif split_type=='group_by_smiles': # Randomly split into train, val, and test sets such that no SMILES is in multiple sets
        gss1 = GroupShuffleSplit(n_splits=2, train_size=0.8, random_state=random_seed)
        train_idx, temp_idx = list(gss1.split(X, groups=X['smiles']))[0]
        X_train, X_temp = X.iloc[train_idx,:], X.iloc[temp_idx,:]
        gss2 = GroupShuffleSplit(n_splits=2, train_size=0.5, random_state=random_seed)
        val_idx, test_idx = list(gss2.split(X_temp, groups=X_temp['smiles']))[0]
        X_val, X_test = X_temp.iloc[val_idx, :], X_temp.iloc[test_idx, :]
    elif split_type=='random': # Randomly split into train, val, and test sets
        X_train = X.sample(frac=0.8, random_state=random_seed)
        X_temp = X.drop(X_train.index)
        X_val = X_temp.sample(frac=0.5, random_state=random_seed)
        X_test = X_temp.drop(X_val.index)

    if scale_targets:
        scaler = StandardScaler()
        scaler.fit(X_train[['target_names']])
        X_train[['target_names']] = scaler.transform(X_train[['target_names']])
        X_val[['target_names']] = scaler.transform(X_val[['target_names']])
        X_test[['target_names']] = scaler.transform(X_test[['target_names']])

    if write_files:
        # Name files
        train_target_file = 'smiles_target_train.csv'
        val_target_file = 'smiles_target_val.csv'
        test_target_file = 'smiles_target_test.csv'
        train_features_file = 'features_train.csv'
        val_features_file = 'features_val.csv'
        test_features_file = 'features_test.csv'

        # Write splits to CSVs
        if solvation:
            X_train[['smiles','solvent']+target_names].to_csv(train_target_file, index=False)
            X_val[['smiles','solvent']+target_names].to_csv(val_target_file, index=False)
            X_test[['smiles','solvent']+target_names].to_csv(test_target_file, index=False)
        else:
            X_train[['smiles']+target_names].to_csv(train_target_file, index=False)
            X_val[['smiles']+target_names].to_csv(val_target_file, index=False)
            X_test[['smiles']+target_names].to_csv(test_target_file, index=False)
        if feature_names:
            X_train[feature_names].to_csv(train_features_file, index=False)
            X_val[feature_names].to_csv(val_features_file, index=False)
            X_test[feature_names].to_csv(test_features_file, index=False)

    return X_train, X_val, X_test


def handle_duplicates(df, cutoff=5, agg_source_col='multiple'):
    """Aggregates duplicate measurements in a DataFrame.

    Parameters
    ----------
    df : pandas DataFrame
        DataFrame with required columns: 'smiles', 'solvent', 'peakwavs_max' 
    cutoff : int
        Wavelength cutoff in nm. Duplicate measurements of the same smiles-solvent
        pair with standard deviation less than cutoff are averaged. Those with 
        standard deviation greater than cutoff are dropped.
        
    Returns
    -------
    df : pandas DataFrame
        An updated DataFrame with duplicates aggregated or removed
        
    """
    
    col_names = ['smiles', 'solvent'] + target_names + ['source']

    cols = [x for x in df.columns if x not in col_names]
    
    agg_dict = {}
    for property in target_names:
        agg_dict[property] = ['mean','std']
    
    if agg_source_col=='multiple':
        agg_dict['source'] = lambda x: 'multiple' if len(x) > 1 else x, 
    elif agg_source_col=='random':
        np.random.seed(0)
        agg_dict['source'] = np.random.choice
        
    for col in cols:
        agg_dict[col] = 'mean'
    
    # For all smiles+solvent pairs, find mean and std of target property/properties
    # If std > cutoff, drop; elif std <= cutoff, take mean
    df = df.groupby(['smiles','solvent']).agg(agg_dict).reset_index()
    for property in target_names:
        high_std_idx = df[df[property]['std']>cutoff].index
        df.drop(index=high_std_idx, inplace=True)

    df.drop(columns='std', level=1, inplace=True)
    df.columns = df.columns.get_level_values(0)
    
    return df

# Set initial directory
DATA_DIR = os.getcwd()

# Read in data files
if len(optical_properties) == 1:
    if 'absPeak' in optical_properties:
        file_name = 'data_same_test_set_abs.csv'
    elif 'emiPeak' in optical_properties:
        file_name = 'data_same_test_set_emi.csv'
elif 'absPeak' in optical_properties and 'emiPeak' in optical_properties:
    file_name = 'data_same_test_set_abs_emi.csv'

property_df = pd.read_csv(f'processed/{file_name}')
# wb97xd3_df = pd.read_csv('computed/20210109_computed_df_all.csv')

# Filter data
lower_cutoff = 0.9 # eV
upper_cutoff = 10 # eV
# wb97xd3_df = wb97xd3_df.loc[(wb97xd3_df['energy_max_osc']>lower_cutoff) & (wb97xd3_df['energy_max_osc']<upper_cutoff)].copy()

# Transform lifetime column in the df so it is log(lifetime)
if 'logLife' in optical_properties:
    property_df['log_lifetime'] = np.log10(property_df['log_lifetime'])

# Put splits in corresponding directories
if optical_properties == ['absPeak']:  
    directory_name = 'lambda_max_abs'
elif optical_properties == ['emiPeak']:
    directory_name = 'lambda_max_emi'
elif optical_properties == ['absPeak', 'emiPeak']:
    directory_name = 'both_peaks'
elif optical_properties == ['absPeak', 'absBand', 'absMol']:
    directory_name = 'abs_all'
elif optical_properties == ['emiPeak', 'emiBand']:
    directory_name = 'emi_all'
elif optical_properties == ['absPeak', 'absBand', 'absMol', 'emiPeak', 'emiBand']:
    directory_name = 'multitask_peak_stats'
elif optical_properties == ['absPeak', 'absBand', 'absMol', 'emiPeak', 'emiBand', 'quantumYield', 'logLife']:
    directory_name = 'multitask_all'
elif optical_properties == ['quantumYield']:
    directory_name = 'quantum_yield'
elif optical_properties == ['logLife']:
    directory_name = 'log_lifetime'

for split_type in ['random', 'group_by_smiles', 'scaffold']:
    os.chdir(os.path.join(DATA_DIR,f'splits_same_test_set/{directory_name}/deep4chem/{split_type}'))
    deep4chem_df = property_df.loc[property_df['source']=='deep4chem', :]
    _, _, _ = data_split_and_write(deep4chem_df, feature_names=None, target_names=target_names, solvation=True, 
                                   split_type=split_type, scale_targets=False, write_files=True, random_seed=0)


# highest_tddft_peak 
# for split_type in ['random', 'scaffold']:
#     os.chdir(os.path.join(DATA_DIR,f'splits_same_test_set/highest_tddft_peak/20210109_wb97xd3/{split_type}'))
#     _, _, _ = data_split_and_write(wb97xd3_df, feature_names=None, target_names=['energy_max_osc'], solvation=False, 
#                                    split_type=split_type, scale_targets=False, write_files=True, random_seed=0)

