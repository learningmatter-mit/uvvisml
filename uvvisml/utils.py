import numpy as np
import pandas as pd
import os
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from rdkit.Chem import AllChem as Chem
from rdkit.DataStructs import ConvertToNumpyArray

def get_morgan_fingerprints(df, mol_or_solv='molecules', nbits=None):
    """Gets Morgan fingerprints for a dataframe with SMILES columns.

    Parameters
    ----------
    df : pandas DataFrame
        A DataFrame that contains columns of 'smiles' and/or 'solvent'
    mol_or_solv : 'molecules' or 'solvents'
        A flag to specify which column to look for and what default
        value of nbits to use
    nbits : int
        Number of bits for Morgan fingerprint (default is 1024 for smiles
        and 256 for solvent)

    Returns
    -------
    df : pandas DataFrame
        An updated DataFrame including the Morgan fingerprints, one bit 
        per column
    col_names_list : list of str
        A list of the names of the Morgan fingerprint columns ('mfpX' 
        or 'sfpX' for X between 0 and nbits)
        
    """
    
    if mol_or_solv=='molecules':
        radius = 4
        if nbits is None:
            nbits = 1024
        col_name = 'mfp'
        smiles_col = 'smiles'
    elif mol_or_solv=='solvents':
        radius = 4
        if nbits is None:
            nbits = 256
        col_name = 'sfp'
        smiles_col = 'solvent'

    unique_df = df.drop_duplicates(subset=[smiles_col])[[smiles_col]]
    smiles_list = list(unique_df[smiles_col])

    fps = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        arr = np.zeros((0,), dtype=np.int8)
        fp = Chem.GetMorganFingerprintAsBitVect(mol,radius,nbits)
        ConvertToNumpyArray(fp, arr)
        fps.append(arr)
    
    col_names_list = []
    for i in range(0,nbits):
        unique_df[col_name+str(i+1)] = np.nan
        col_names_list.append(col_name+str(i+1))
    
    unique_df[col_names_list] = fps

    df = df.merge(unique_df)

    return df, col_names_list

def calculate_loss_metrics(results_dir, model, verbose=False):
    """Calculate the MAE, RMSE, and R2 for a model's predictions.

    Parameters
    ----------
    results_dir : str
        Directory where results are stored
    model : str
        'chemprop' or 'xgboost' 
    verbose : bool
        Whether to print messages while calculating metrics
        (default False)
    
    Returns
    -------
    mae : float
        Mean absolute error
    rmse : float
        Root mean square error
    r2 : float
        R^2 score
        
    """
    
    if verbose: 
        print(results_dir)
    
    if (model == 'chemprop') or (model == 'chemprop_tddft'):
        train_df = pd.read_csv(os.path.join(results_dir, 'smiles_target_train.csv'))
        test_df = pd.read_csv(os.path.join(results_dir, 'smiles_target_test.csv'))
        try:
            preds_df = pd.read_csv(os.path.join(results_dir, 'preds.csv'))
        except:
            print(results_dir)
            return np.nan, np.nan, np.nan
        preds_df.rename(columns={'peakwavs_max':'peakwavs_max_pred'}, inplace=True)
        results_df = pd.concat([test_df, preds_df[['peakwavs_max_pred']]], axis=1)
    elif model == 'chemfluor_gbrt':
        results_df = pd.read_csv(os.path.join(results_dir, 'chemfluor_gbrt_preds.csv'))
        
    mae = mean_absolute_error(results_df['peakwavs_max'], results_df['peakwavs_max_pred'])
    rmse = mean_squared_error(results_df['peakwavs_max'], results_df['peakwavs_max_pred'], squared=False)
    r2 = r2_score(results_df['peakwavs_max'], results_df['peakwavs_max_pred'])
    
    if verbose:
        print('MAE: {0:.2f}, RMSE: {1:.2f}, R2: {2:.2f}'.format(mae, rmse, r2))

    # Set extreme outliers to have predicted value equal to the mean of the training set
    # 4 extreme outlier predictions are present due to erroneous values in the RDKit or TDDFT features
    outlier_idx = results_df.query('peakwavs_max_pred < 0 | peakwavs_max_pred > 2000').index
    if len(outlier_idx)>0:
        bad_smiles = results_df.loc[outlier_idx, 'smiles'].values
        true_value = results_df.loc[outlier_idx, 'peakwavs_max'].values
        pred_value = results_df.loc[outlier_idx, 'peakwavs_max_pred'].values
        mean_of_training_set = train_df['peakwavs_max'].mean() # this will fail if XGBoost has an outlier because we didn't write the training set to a file
        results_df.loc[outlier_idx, 'peakwavs_max_pred'] = mean_of_training_set
        if verbose: 
            print(f'SMILES {bad_smiles} with experimental value(s) {true_value} have bad prediction(s) of {pred_value}')
            print(f'Setting all predictions outside of range 0 - 2000 nm to mean of training set ({mean_of_training_set} nm)')

        mae = mean_absolute_error(results_df['peakwavs_max'], results_df['peakwavs_max_pred'])
        rmse = mean_squared_error(results_df['peakwavs_max'], results_df['peakwavs_max_pred'], squared=False)
        r2 = r2_score(results_df['peakwavs_max'], results_df['peakwavs_max_pred'])
        if verbose:
            print('New MAE: {0:.2f}, New RMSE: {1:.2f}, New R2: {2:.2f}'.format(mae, rmse, r2))
        
    if verbose:    
        print()
        
    return mae, rmse, r2

