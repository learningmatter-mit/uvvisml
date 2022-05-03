import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

opt_properties = ['lambda_max_abs', 'lambda_max_emi', 'both_peaks', 'abs_all', 'emi_all', 'multitask_peak_stats', 'multitask_all', 'quantum_yield', 'log_lifetime']
split_types = ['group_by_smiles', 'random', 'scaffold']

prop_to_col_name = {'lambda_max_abs': 'peakwavs_max',
                   'lambda_max_emi': 'emi_peakwavs_max',
                   'both_peaks': ['abs_peakwavs_max', 'emi_peakwavs_max'],
                    'abs_all': ['abs_peakwavs_max', 'abs_bandwidth', 'abs_molar_ext_coeff'],
                    'emi_all': ['emi_peakwavs_max', 'emi_bandwidth'],
                    'multitask_peak_stats': ['abs_peakwavs_max', 'abs_bandwidth', 'abs_molar_ext_coeff', 'emi_peakwavs_max', 'emi_bandwidth'],
                   'multitask_all': ['abs_peakwavs_max', 'abs_bandwidth', 'abs_molar_ext_coeff', 'emi_peakwavs_max', 'emi_bandwidth', 'quantum_yield', 'log_lifetime'],
                    'quantum_yield': 'quantum_yield',
                    'log_lifetime': 'log_lifetime'}

col_units = {'peakwavs_max': 'nm',
           'emi_peakwavs_max': 'nm',
           'abs_peakwavs_max': 'nm',
            'abs_bandwidth': 'nm',
             'abs_molar_ext_coeff': '$mol^{-1}$ $dm^3$ $cm^{-1}$',
            'emi_bandwidth': 'nm',
            'quantum_yield': '',
            'log_lifetime': 'ns'}

my_order = {'lambda_max_abs':'1', 'lambda_max_emi':'1', 'both_peaks':'2', 'abs_all':'3', 'emi_all':'3', 'multitask_peak_stats':'4', 'multitask_all':'5', 'quantum_yield':'1', 'log_lifetime':'1'}

f = open('prediction_metrics.csv', 'w')
f.write('property,split,combo,rmse,mae,r2\n')

def metrics_only(preds_file, true_file, col_name):
    preds_df = pd.read_csv(preds_file)
    true_df = pd.read_csv(true_file)

    true_value = true_df[col_name]
    pred_value = preds_df[col_name]
    
    metrics = calc_metrics(true_value, pred_value)
    return metrics

def calc_metrics(true_value, predicted_value):
    rms = round(mean_squared_error(true_value, predicted_value, squared=False), 7)
    mae = round(mean_absolute_error(true_value, predicted_value), 7)
    r2 = round(r2_score(true_value, predicted_value), 7)
    
    result = str(rms) + ',' + str(mae) + ',' + str(r2) + '\n'
    return result

for opt_prop in opt_properties:
    for split_type in split_types:
        preds_file = 'uvvisml/models/'+ opt_prop + '_checkpoints/' + split_type + '/' + opt_prop + '_preds.csv'
        true_file = 'uvvisml/data/splits/'+ opt_prop + '/deep4chem/' + split_type + '/smiles_target_test.csv'
        col_names = prop_to_col_name[opt_prop]
        if isinstance(col_names, list):
            for n in col_names:
                col_name = n
                new_str = col_name + ',' + split_type + ',' + opt_prop + ',' + metrics_only(preds_file, true_file, col_name)
                f.write(new_str)
        else:
            col_name = col_names
            if col_name == 'peakwavs_max':
                img_name_col_name = 'abs_peakwavs_max'
            else:
                img_name_col_name = col_name
            new_str = img_name_col_name + ',' + split_type + ',' + 'alone' + ',' + metrics_only(preds_file, true_file, col_name)
            f.write(new_str)