#!/bin/bash
#SBATCH -p normal
#SBATCH -J uvvis_prod_combined
#SBATCH -o uvvis_prod_combined-%j.out
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

CHEMPROP_DIR='/home/gridsan/kgreenman/chemprop'
MODEL_DIR='../../../..'
SPLITS_DIR='../../../../../data/splits'

#python $CHEMPROP_DIR/train.py --data_path $SPLITS_DIR/lambda_max_abs/combined/group_by_smiles/smiles_target_train.csv --separate_val_path $SPLITS_DIR/lambda_max_abs/combined/group_by_smiles/smiles_target_val.csv --separate_test_path $SPLITS_DIR/lambda_max_abs/combined/group_by_smiles/smiles_target_test.csv --dataset_type regression --save_dir $(pwd) --metric rmse --epochs 200 --gpu 0 --ensemble_size 5 --config_path ../sigopt_chemprop_lambda_max_best_hyperparams_small.json --number_of_molecules 2

python $CHEMPROP_DIR/predict.py --test_path $SPLITS_DIR/lambda_max_abs/combined/group_by_smiles/smiles_target_test.csv --checkpoint_dir $(pwd) --preds_path preds.csv --gpu 0 --number_of_molecules 2 --ensemble_variance
