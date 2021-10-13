import os, subprocess
import argparse
import logging

def write_header(cluster=None):
    if cluster == 'supercloud':
        header = """#!/bin/bash
#SBATCH -p normal
#SBATCH -J uvvis_pred
#SBATCH -o uvvis_pred-%j.out
#SBATCH -t 1:00:00
#SBATCH -n 1
#SBATCH -N 1
#SBATCH --mem=10gb
#SBATCH --gres=gpu:volta:1

echo "Date              = $(date)"
echo "Hostname          = $(hostname -s)"
echo "Working Directory = $(pwd)"
echo ""
cat $0
echo ""

source /etc/profile
module load anaconda/2021a
source activate chemprop

"""

    elif cluster == 'engaging':
        header = """#!/bin/bash
#SBATCH -p sched_mit_rafagb,sched_mit_rafagb_amd
#SBATCH -J uvvis_pred
#SBATCH -o uvvis_pred-%j.out
#SBATCH -t 1:00:00
#SBATCH -n 1
#SBATCH -N 1
#SBATCH --mem=10gb
#SBATCH --gres=gpu:1

echo "Date              = $(date)"
echo "Hostname          = $(hostname -s)"
echo "Working Directory = $(pwd)"
echo ""
cat $0
echo ""

module load anaconda3/2020.11
source activate chemprop

"""

    elif cluster is None:
        header = """#!/bin/bash

conda activate chemprop

"""

    return header

def choose_model(args):

    module_dir = os.path.dirname(os.path.abspath(__file__))
    
    if args.property == 'absorption_peak_nm_expt':
        prop = 'lambda_max_abs'
    elif args.property == 'vertical_excitation_eV_tddft':
        prop = 'lambda_max_abs_wb97xd3'

    # Don't allow TDDFT dataset to be specified with experimental property or vice versa
    if (args.property == 'absorption_peak_nm_expt') and (args.train_dataset == 'all_wb97xd3'):
        raise ValueError(f'Cannot use computed dataset {args.train_dataset} to predict experimental property {args.property}')
    if (args.property == 'vertical_excitation_eV_tddft') and ((args.train_dataset == 'combined') or (args.train_dataset == 'deep4chem')):
        raise ValueError(f'Cannot use experimental dataset {args.train_dataset} to predict computed property {args.property}')

    # Don't allow ChempropTDDFT method to be specified for predicting TDDFT property only
    if (args.property == 'vertical_excitation_eV_tddft') and (args.method == 'chemprop_tddft'):
        raise ValueError('Cannot use ChempropTDDFT to predict TDDFT property only. This model uses TDDFT as a feature to predict experiment.')
    
    # Choose default model for given property-method pair unless train dataset specified
    if args.train_dataset:
        dataset = args.train_dataset
    else:
        if args.property == 'absorption_peak_nm_expt':
            dataset = 'combined'
        elif args.property == 'vertical_excitation_eV_tddft':
            dataset = 'all_wb97xd3'

    model_checkpoint_dir = os.path.join(module_dir, 'models', prop, args.method, dataset, 'production', 'fold_0')

    return model_checkpoint_dir

def write_script(args, header, model_checkpoint_dir):

    if args.method == 'chemprop_tddft':
        module_dir = os.path.dirname(os.path.abspath(__file__))
        tddft_model_dir = os.path.join(module_dir, "models/lambda_max_abs_wb97xd3/chemprop/all_wb97xd3/production/fold_0/")
        tddft_predict_command = f"""chemprop_predict --test_path {args.test_file} --checkpoint_dir {tddft_model_dir} \
--preds_path test_tddft_preds.csv

python {module_dir}/models/tddft_to_features_file.py

"""

    predict_command = f"""chemprop_predict --test_path {args.test_file} \
--checkpoint_dir {model_checkpoint_dir} --preds_path {args.preds_file}"""

    if args.property in ['absorption_peak_nm_expt']: # if predicting experimental property (not in vacuum)
        predict_command += ' --number_of_molecules 2'

    if args.gpu:
        predict_command += ' --gpu 0'
    
    if args.uncertainty_method == 'ensemble_variance':
        predict_command += ' --ensemble_variance'

    if args.method == 'chemprop_tddft':
        predict_command += ' --features_path features_test.csv'
        command = header + tddft_predict_command + predict_command
    else:
        command = header + predict_command

    script_name = 'run_chemprop.sh'
    with open(script_name,'w') as f:
        f.write(command)

    return script_name

def run_script(script_name, cluster=None):
    if cluster in ['supercloud','engaging']:
        run_command = f'sbatch {script_name}'
    elif cluster is None:
        run_command = f'bash -i {script_name}'

    process = subprocess.Popen(run_command.split())
    process.communicate()

    return

def get_parser():
    parser = argparse.ArgumentParser(description='Predicts UVVis properties of molecules using existing Chemprop models')
    parser.add_argument('--test_file', type=str, default='smiles_target_test.csv',
                        help='Path to CSV file with columns named "smiles" and "solvent" (for experiment) or "smiles" only (for TD-DFT)')
    parser.add_argument('--property', type=str, default='absorption_peak_nm_expt',
                        choices=['absorption_peak_nm_expt','vertical_excitation_eV_tddft'],
                        help='Name of property to predict')
    parser.add_argument('--method', type=str, default='chemprop',
                        choices=['chemprop','chemprop_tddft'],
                        help='Type of model to use for predictions')
    parser.add_argument('--train_dataset', type=str, default=None,
                        choices=['deep4chem','combined','all_wb97xd3'],
                        help='Predict using the model trained on this dataset (can override default for a given property-method pair)')
    parser.add_argument('--cluster', type=str, default=None, choices=[None,'supercloud','engaging'],
                        help='Name of cluster script will run on, to choose Slurm header, if applicable')
    parser.add_argument('--preds_file', type=str, default='preds.csv',
                        help='File to which prediction results should be saved')
    parser.add_argument('--gpu', default=False, action='store_true',
                        help='Specify if device has access to a GPU')
    parser.add_argument('--uncertainty_method', type=str, default='ensemble_variance',
                        choices=['ensemble_variance'],
                        help='Method for calculating uncertainty in model predictions')
    parser.add_argument('--log_level', type=str, default='warning',
                        choices=['debug','info','warning','error','critical'],
                        help='Specify what level of logging to print to console')
    return parser

def main(args):
    numeric_level = getattr(logging, args.log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(level=numeric_level)

    logging.info('Choosing header for script...')
    header = write_header(args.cluster)

    logging.info('Choosing model...')
    model_checkpoint_dir = choose_model(args)

    logging.info('Writing script to file...')
    script_name = write_script(args, header, model_checkpoint_dir)

    logging.info('Running script file...')
    run_script(script_name, args.cluster)
    return

if __name__ == '__main__':
    # Command Line Argument Parsing
    parser = get_parser()
    args = parser.parse_args()

    main(args)
