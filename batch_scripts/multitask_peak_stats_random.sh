#!/bin/bash
#SBATCH -p normal
#SBATCH -J multitask_peak_stats_random
#SBATCH -o multitask_peak_stats_random-%j.out
#SBATCH -t 1-00:00:00
#SBATCH -n 1
#SBATCH -N 1
#SBATCH --mem=50gb
#SBATCH --gres=gpu:volta:1

echo "Date              = $(date)"
echo "Hostname          = $(hostname -s)"
echo "Working Directory = $(pwd)"
echo ""
cat $0
echo ""

source /etc/profile
module load anaconda/2021b
source activate uvvisml

python3 predict2.py multitask_peak_stats random
