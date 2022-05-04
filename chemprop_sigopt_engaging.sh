#!/bin/bash
#SBATCH -p sched_mit_rafagb,sched_mit_rafagb_amd
#SBATCH -J chemprop_sigopt
#SBATCH -o chemprop_sigopt-%j.out
#SBATCH -t 3-00:00:00
#SBATCH -n 1
#SBATCH -N 1
#SBATCH --mem=30gb
#SBATCH --gres=gpu:1
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=kimele03@mit.edu

echo "Date              = $(date)"
echo "Hostname          = $(hostname -s)"
echo "Working Directory = $(pwd)"
echo ""

module load anaconda3/2020.11
source activate chemprop

MODEL_DIR = '../..'
SPLITS_DIR = '../../../data/splits'

python $MODEL_DIR/chemprop_sigopt_engaging.py --data_path $SPLITS_DIR/lambda_max_abs/deep4chem/group_by_smiles/smiles_target_train.csv --separate_val_path $SPLITS_DIR/lambda_max_abs/deep4chem/group_by_smiles/smiles_target_val.csv --separate_test_path $SPLITS_DIR/lambda_max_abs/deep4chem/group_by_smiles/smiles_target_test.csv --metric rmse --epochs 50 --name lambda_max --observation_budget 50 --save_dir $(pwd) --solvation