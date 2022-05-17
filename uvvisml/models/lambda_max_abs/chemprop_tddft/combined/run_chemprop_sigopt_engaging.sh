#!/bin/bash
#SBATCH -p sched_mit_rafagb,sched_mit_rafagb_amd
#SBATCH -J chemprop_sigopt_combined_tddft
#SBATCH -o chemprop_sigopt_combined_tddft-%j.out
#SBATCH -t 4-00:00:00
#SBATCH -n 1
#SBATCH -N 1
#SBATCH --mem=10gb
#SBATCH --gres=gpu:1
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=kpg@mit.edu

echo "Date              = $(date)"
echo "Hostname          = $(hostname -s)"
echo "Working Directory = $(pwd)"
echo ""

module load anaconda3/2020.11
source activate chemprop

MODEL_DIR='../../..'
SPLITS_DIR='../../../../data/splits'
CHEMPROP_DIR="/home/kpg/chemprop"
tddft_model_dir="../../../lambda_max_abs_wb97xd3/chemprop/all_wb97xd3/production/fold_0/"

# Predict Using TD-DFT Model
python $CHEMPROP_DIR/predict.py --test_path $SPLITS_DIR/lambda_max_abs/combined/group_by_smiles/smiles_target_train.csv --checkpoint_dir $tddft_model_dir --preds_path train_tddft_preds.csv
python $CHEMPROP_DIR/predict.py --test_path $SPLITS_DIR/lambda_max_abs/combined/group_by_smiles/smiles_target_val.csv --checkpoint_dir $tddft_model_dir --preds_path val_tddft_preds.csv
python $CHEMPROP_DIR/predict.py --test_path $SPLITS_DIR/lambda_max_abs/combined/group_by_smiles/smiles_target_test.csv --checkpoint_dir $tddft_model_dir --preds_path test_tddft_preds.csv

# Convert Output of TD-DFT Model to Feature File Inputs
python $MODEL_DIR/tddft_to_features_file.py

# Run Hyperparameter Optimization for Experimental Model
python $MODEL_DIR/chemprop_sigopt_engaging.py --data_path $SPLITS_DIR/lambda_max_abs/combined/group_by_smiles/smiles_target_train.csv --separate_val_path $SPLITS_DIR/lambda_max_abs/combined/group_by_smiles/smiles_target_val.csv --separate_test_path $SPLITS_DIR/lambda_max_abs/combined/group_by_smiles/smiles_target_test.csv --metric rmse --epochs 50 --name lambda_max --observation_budget 50 --save_dir $(pwd) --solvation --features_path features_train.csv --separate_val_features_path features_val.csv --separate_test_features_path features_test.csv
