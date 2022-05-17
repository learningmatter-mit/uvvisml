#!/bin/bash
#SBATCH -p sched_mit_rafagb,sched_mit_rafagb_amd
#SBATCH -J abs_all_group_by_smiles
#SBATCH -o abs_all_group_by_smiles-%j.out
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

python chemprop_sigopt_engaging.py --data_path smiles_target_test.csv --separate_val_path smiles_target_val.csv --separate_test_path smiles_target_test.csv --metric rmse --name abs_all --observation_budget 50 --save_dir $(pwd)
