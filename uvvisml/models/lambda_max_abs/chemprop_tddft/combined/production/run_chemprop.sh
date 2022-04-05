#!/bin/bash
#SBATCH -p normal
#SBATCH -J uvvis_tddft_combined_prod
#SBATCH -o uvvis_tddft_combined_prod-%j.out
#SBATCH -t 5-00:00:00
#SBATCH -n 1
#SBATCH -N 1
#SBATCH --mem=30gb
#SBATCH --gres=gpu:volta:1

echo "Date              = $(date)"
echo "Hostname          = $(hostname -s)"
echo "Working Directory = $(pwd)"
echo ""
cat $0
echo ""

source /etc/profile
module load anaconda/2020a
source activate chemprop

MODEL_DIR='../../../..'
SPLITS_DIR='../../../../../data/splits'
CHEMPROP_DIR='/home/gridsan/kgreenman/chemprop'
tddft_model_dir="../../../../lambda_max_abs_wb97xd3/chemprop/all_wb97xd3/production/fold_0/"

# Predict Using TD-DFT Model
python $CHEMPROP_DIR/predict.py --test_path $SPLITS_DIR/lambda_max_abs/combined/group_by_smiles/smiles_target_train.csv --checkpoint_dir $tddft_model_dir --preds_path train_tddft_preds.csv
python $CHEMPROP_DIR/predict.py --test_path $SPLITS_DIR/lambda_max_abs/combined/group_by_smiles/smiles_target_val.csv --checkpoint_dir $tddft_model_dir --preds_path val_tddft_preds.csv
python $CHEMPROP_DIR/predict.py --test_path $SPLITS_DIR/lambda_max_abs/combined/group_by_smiles/smiles_target_test.csv --checkpoint_dir $tddft_model_dir --preds_path test_tddft_preds.csv

# Convert Output of TD-DFT Model to Feature File Inputs
python $MODEL_DIR/tddft_to_features_file.py

# Train Experimental Model
python $CHEMPROP_DIR/train.py --data_path $SPLITS_DIR/lambda_max_abs/combined/group_by_smiles/smiles_target_train.csv --separate_val_path $SPLITS_DIR/lambda_max_abs/combined/group_by_smiles/smiles_target_val.csv --separate_test_path $SPLITS_DIR/lambda_max_abs/combined/group_by_smiles/smiles_target_test.csv --dataset_type regression --save_dir $(pwd) --metric rmse --epochs 200 --gpu 0 --ensemble_size 5 --config_path ../sigopt_chemprop_lambda_max_best_hyperparams_small.json --number_of_molecules 2 --features_path features_train.csv --separate_val_features_path features_val.csv --separate_test_features_path features_test.csv

# Make Experimental Predictions
python $CHEMPROP_DIR/predict.py --test_path $SPLITS_DIR/lambda_max_abs/combined/group_by_smiles/smiles_target_test.csv --checkpoint_dir $(pwd) --preds_path preds.csv --gpu 0 --number_of_molecules 2 --ensemble_variance --separate_test_features_path features_test.csv
