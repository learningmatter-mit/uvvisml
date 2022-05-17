# Documentation

## Data cleaning and organization

In /uvvisml/data, use the `data_organization_and_cleaning_general.py` script to prepare the data. The first argument should be the string 'same_test_set' for using the same test set (and some other string like 'diff_test_set' otherwise), and the following argument(s) should be the optical property(ies).

For example:

    python3 data_organization_and_cleaning_general.py same_test_set absPeak emiPeak

The csv files will be generated in /uvvisml/data/processed.

## Creating train/val/test splits

In /uvvisml/data, use the `create_splits_general.py` script to split the data into a train, validation, and test set. The first argument indicates whether to use the same test set, and the following argument(s) indicate the optical property(ies).

For example:

    python3 create_splits_general.py diff_test_set absPeak emiPeak

The train/val/test splits will be generated in either /uvvisml/data/splits or /uvvisml/data/splits_same_test_set depending on the first argument.

## Making predictions

Use the `predict2.py` script to train the model and create predictions for some optical property or combination of properties.

After typing 'python3 predict2.py', the first argument following afterwards should be the name representing the optical property(ies) (e.g. both_peaks for absPeak and emiPeak), the second argument should be the split type (group_by_smiles, random, or scaffold), and the third argument should be a string for using the same test set (same_test_set or diff_test_set). 

For example:

    python3 predict2.py both_peaks group_by_smiles diff_test_set

## Generating bash scripts

To generate predictions for all of the different optical property and split type combinations, use `generate_bash_general.py` script in /uvvisml/bash_scripts, where the first argument is a string for using the same test set, and the second argument is a string for hyperparameter optimization.

For example:

    python3 generate_bash_general.py same_test_set not

The bash scripts will be generated in their respective directories in /uvvisml/models (e.g. `lambda_max_abs_group_by_smiles_hyperparam_opt.sh` in /uvvisml/models/lambda_max_abs_checkpoints/group_by_smiles).

Submit jobs that run each of these bash scripts in SuperCloud using the `sbatch` command.

## Visualizing prediction plots and metrics

In /prediction_plots_and_metrics/, you can use `prediction_plots_and_metrics.ipynb` to view scatter plots of predicted vs. true values for each optical property given the optical property combination and split type that it was predicted with. 

After running the cells, each of the figures should be saved as a png file in either /prediction_plots_and_metrics/prediction_plots_images or /prediction_plots_and_metrics/prediction_plots_images_same_test_set, depending on the cell you run. 

Use `generate_image_table_general.py` to write a markdown file containing a table of the figures. The first argument after 'python3 generate_image_table_general.py' should be a string for using the same test set.

For example:

    python3 generate_image_table_general.py same_test_set

The markdown file will be generated in the current directory.

## Hyperparameter optimization

Similar to making predictions, use `generate_bash_general.py` script in /uvvisml/bash_scripts to create bash scripts for all of the different optical property and split type combinations.

For example:

    python3 generate_bash_general.py diff_test_set hyperparam_opt

Submit jobs that run each of these bash scripts in Engaging using the `sbatch` command. The results can be viewed under 'Experiments' when logged into your SigOpt account.