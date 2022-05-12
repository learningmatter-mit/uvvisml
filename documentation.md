# Documentation

## Data cleaning and organization

Use the data_organization_and_cleaning_general.py script to prepare the data. The first argument should be a boolean for using the same test set, and the following argument(s) should be the optical property(ies).

For example:

    python3 data_organization_and_cleaning_general.py true absPeak emiPeak



## Creating train/val/test splits

Use the create_splits_general.py script to split the cleaned data into a train, validation, and test set.

For example:

    python3 create_splits_general.py true absPeak emiPeak

## Making predictions

Use the predict2.py script to train the model and create predictions for some optical property or combination of properties. Login to your SuperCloud account and submit a job to use SuperCloud's 

After typing 'python3 predict2.py', the first argument following afterwards should be the optical property(ies), the second argument should be the split type, and the third argument should be a boolean for using the same test set. 

For example:

    python3 predict2.py both_peaks group_by_smiles true

