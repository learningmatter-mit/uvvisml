import pandas as pd
import os
import logging

for set_type in ['train','val','test']:
    tddft_preds_file_name = f'{set_type}_tddft_preds.csv'
    if os.path.exists(tddft_preds_file_name):
        df = pd.read_csv(tddft_preds_file_name)
        df.rename(columns={'energy_max_osc':'peakwavs_max_tddft_pred'}, inplace=True)
        feature_cols = [x for x in df.columns if x not in ['smiles','solvent','peakwavs_max']]
        df['peakwavs_max_tddft_pred'] = 1240/df['peakwavs_max_tddft_pred'] # convert to nm
    
        if os.path.exists(f'features_{set_type}.csv'): # add column to existing features file
            logging.warning('TD-DFT predictions are being concatentated onto an existing features file. This will cause unexpected behavior if the existing features file is left over from a previous TD-DFT prediction run.')
            features_df = pd.read_csv(f'features_{set_type}.csv')
            orig_feature_cols = [x for x in features_df.columns if x not in ['smiles','solvent','peakwavs_max']]
            all_features_df = pd.concat([features_df[orig_feature_cols],df[feature_cols]], axis=1)
            all_features_df.to_csv(f'features_{set_type}.csv', index=False)
        else: # make new feature file
            df[feature_cols].to_csv(f'features_{set_type}.csv', index=False)
