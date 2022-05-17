#!/bin/bash
#SBATCH -p sched_mit_rafagb,sched_mit_rafagb_amd,sched_any_quicktest
#SBATCH -J chemprop_sigopt
#SBATCH -o chemprop_sigopt-%j.out
#SBATCH -t 15:00
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

python /home/kpg/chemprop/train.py --data_path ../../../../data/splits/lambda_max_abs/deep4chem/group_by_smiles/smiles_target_train.csv --dataset_type regression --save_dir /home/kpg/uvvisml/uvvisml/models/lambda_max_abs/chemprop/deep4chem/results/418174/44970063 --config_path /home/kpg/uvvisml/uvvisml/models/lambda_max_abs/chemprop/deep4chem/results/418174/44970063/hyperopt.json --metric rmse --epochs 10 --gpu 0 --ensemble_size 1 --separate_val_path ../../../../data/splits/lambda_max_abs/deep4chem/group_by_smiles/smiles_target_val.csv --separate_test_path ../../../../data/splits/lambda_max_abs/deep4chem/group_by_smiles/smiles_target_test.csv --number_of_molecules 2
