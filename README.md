UVVisML
==============================
[//]: # (Badges)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


Predict optical properties of molecules with machine learning.

## Setup
0. Install [Anaconda or Miniconda](https://docs.conda.io/projects/continuumio-conda/en/latest/user-guide/install/index.html) if you have not yet done so.
1. `git clone git@github.com:learningmatter-mit/uvvisml.git`
2. `cd uvvisml`
3. `conda env create -f uvvisml_env.yml`
4. `cd uvvisml`
4. `bash get_model_files.sh`
5. `conda activate uvvisml`

## Making Predictions

### Test file
To make predictions, specify a `--test_file` with the dyes or dye-solvent pairs for which you wish to predict properties. This should be a CSV with one dye (for vacuum TD-DFT predictions) or dye-solvent pair (for experimental predictions) per line. For example, the test file for vacuum TD-DFT predictions could be:
```
smiles
CCN(CC)c1ccc2c(C(F)(F)F)cc(=O)oc2c1
CCN(CC)c1ccc2c(C(F)(F)F)cc(=O)oc2c1
CCN(CC)c1ccc2c(C(F)(F)F)cc(=O)oc2c1
CCN(CC)c1ccc2c(C(F)(F)F)cc(=O)oc2c1
CCN(CC)c1ccc2c(C(F)(F)F)cc(=O)oc2c1
CCN(CC)c1ccc2cc(-c3nc4ccccc4n3C)c(=O)oc2c1
C[SiH](C)c1cccc2ccccc12
```

The test file for experimental predictions could be:
```
smiles,solvent
CCN(CC)c1ccc2c(C(F)(F)F)cc(=O)oc2c1,C1CCCCC1
CCN(CC)c1ccc2c(C(F)(F)F)cc(=O)oc2c1,CCOC(C)=O
CCN(CC)c1ccc2c(C(F)(F)F)cc(=O)oc2c1,CC#N
CCN(CC)c1ccc2c(C(F)(F)F)cc(=O)oc2c1,CCO
CCN(CC)c1ccc2c(C(F)(F)F)cc(=O)oc2c1,OCC(O)CO
CCN(CC)c1ccc2cc(-c3nc4ccccc4n3C)c(=O)oc2c1,CC#N
C[SiH](C)c1cccc2ccccc12,C1CCCCC1
```

### Property
* Experimental peak wavelength of maximum absorption: `--property absorption_peak_nm_expt`
* Vertical excitation energy with maximum oscillator strength in vacuum TD-DFT: `--property vertical_excitation_eV_tddft`

### Method
* Single-fidelity (experiment or TD-DFT): `--method chemprop`
* Multi-fidelity (experiment only): `--method chemprop_tddft`

### Train dataset
* Experiment: `--train_dataset combined` (default) or `--train_dataset deep4chem`
* TD-DFT: `--train_dataset all_wb97xd3`

### Cluster
Cluster that the script will be run on. Includes options for Supercloud and Engaging clusters at MIT. Default of `None` runs the script on the local machine.

### Uncertainty in Predictions
Output the ensemble variance (a measure of epistemic uncertainty) in predictions using `--uncertainty_method ensemble_variance`.

### Examples
```
python ../predict.py --test_file ../data/splits/lambda_max_abs/deep4chem/group_by_smiles/smiles_target_test.csv --property absorption_peak_nm_expt --method chemprop --preds_file test_preds.csv

python ../predict.py --test_file ../data/splits/lambda_max_abs/deep4chem/group_by_smiles/smiles_target_test.csv --property vertical_excitation_eV_tddft --method chemprop --preds_file test_preds.csv

python ../predict.py --test_file ../data/splits/lambda_max_abs/deep4chem/group_by_smiles/smiles_target_test.csv --property absorption_peak_nm_expt --method chemprop --preds_file test_preds.csv --train_dataset deep4chem

python ../predict.py --test_file ../data/splits/lambda_max_abs/deep4chem/group_by_smiles/smiles_target_test.csv --property absorption_peak_nm_expt --method chemprop_tddft --preds_file test_preds.csv --log_level info
```

## Data
Please see the [Data README](uvvisml/data/README.md) for details on the sources and processing of the data used in this repository.

## Citation
If you use this code, please cite the following manuscript:

```
@article{Greenman2021,
  title={Multi-fidelity prediction of molecular optical peaks with deep learning},
  author={Greenman, Kevin P. and Green, William H. and G{\'{o}}mez-Bombarelli, Rafael},
  journal={arXiv preprint arXiv:XXXX.XXXXX},
  year={2021}
}
```
