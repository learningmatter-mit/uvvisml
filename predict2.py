import chemprop
import sys

# command line arguments passed to the program, where first arg is optical property(ies) and second arg is split type
properties_split = sys.argv[1:] #e.g. both_peaks scaffold
optical_properties = properties_split[0]
split_type = properties_split[1] #group_by_smiles, random, or scaffold

# Train model

arguments = [
    '--data_path', f'../uvvisml/data/splits/{optical_properties}/deep4chem/{split_type}/smiles_target_train.csv',
    '--separate_val_path', f'../uvvisml/data/splits/{optical_properties}/deep4chem/{split_type}/smiles_target_val.csv',
    '--separate_test_path', f'../uvvisml/data/splits/{optical_properties}/deep4chem/{split_type}/smiles_target_test.csv',
    '--dataset_type', 'regression',
    '--save_dir', f'../uvvisml/models/{optical_properties}_checkpoints/{split_type}',
    '--epochs', '100', #100-200
    '--gpu', '0',
    '--number_of_molecules', '2',
    '--smiles_columns', 'smiles', 'solvent'
]

train_args = chemprop.args.TrainArgs().parse_args(arguments)
mean_score, std_score = chemprop.train.cross_validate(args=train_args, train_func=chemprop.train.run_training)

# Predict from file

arguments = [
    '--test_path', f'../uvvisml/data/splits/{optical_properties}/deep4chem/{split_type}/smiles_target_test.csv',
    '--preds_path', f'../uvvisml/models/{optical_properties}_checkpoints/{split_type}/{optical_properties}_preds.csv',
    '--checkpoint_dir', f'../uvvisml/models/{optical_properties}_checkpoints/{split_type}',
    '--number_of_molecules', '2',
    '--smiles_columns', 'smiles', 'solvent'
]

predict_args = chemprop.args.PredictArgs().parse_args(arguments)
preds = chemprop.train.make_predictions(args=predict_args)
