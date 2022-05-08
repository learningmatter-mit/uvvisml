#!/home/kpg/.conda/envs/chemprop/bin/python

import json, os, subprocess
import numpy as np
from sigopt import Connection
import argparse

# Evaluate model with the suggested parameter assignments
def evaluate_chemprop_model(assignments, save_dir, args):
    # Transform LRs because experiment set up to keep init and final below max without using linear constraints
    assignments['init_lr'] = assignments['init_lr']*assignments['max_lr']
    assignments['final_lr'] = assignments['final_lr']*assignments['max_lr']

    hyperopt_config_dir = os.path.join(save_dir,"hyperopt.json")
    with open(hyperopt_config_dir, "w") as outfile:  
        json.dump(assignments, outfile)
    
    run_command = f"""/home/kpg/.conda/envs/chemprop/bin/python /home/kpg/chemprop/train.py \
--data_path {args.data_path} \
--dataset_type regression \
--save_dir {save_dir} \
--config_path {hyperopt_config_dir} \
--metric {args.metric} \
--epochs {args.epochs} \
--gpu 0 \
--ensemble_size 1"""

    if args.separate_val_path and args.separate_test_path:
        run_command = run_command + f" --separate_val_path {args.separate_val_path} --separate_test_path {args.separate_test_path}"
    if args.solvation:
        run_command = run_command + " --number_of_molecules 2"
    if args.features_path:
        run_command = run_command + f" --features_path {args.features_path}"
    if args.separate_val_features_path and args.separate_test_features_path:
        run_command = run_command + f" --separate_val_features_path {args.separate_val_features_path} --separate_test_features_path {args.separate_test_features_path}"

    process = subprocess.Popen(run_command.split(), 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                              )
    stdout, stderr = process.communicate()

    results_file = os.path.join(save_dir,"verbose.log")
    with open(results_file, 'r') as f:
        results = f.readlines()
    final_val_score = np.mean([float(y.split()[6]) for y in [x for x in results if f'best validation {args.metric}' in x]])
    
    return final_val_score

def get_parser():
    parser = argparse.ArgumentParser(description='Runs SigOpt to optimize hyperparameters of a Chemprop model')
    parser.add_argument('--data_path', type=str, default='smiles_target_train.csv',
                        help='training data (if validation and test files are specified) or all data (if no validation and test files are specified)')
    parser.add_argument('--separate_val_path', type=str, default=None,  
                        help='validation data')
    parser.add_argument('--separate_test_path', type=str, default=None,
                        help='test data')
    parser.add_argument('--features_path', type=str, default=None,
                        help='path to features file')
    parser.add_argument('--separate_val_features_path', type=str, default=None,
                        help='path to validation features file')
    parser.add_argument('--separate_test_features_path', type=str, default=None,
                        help='path to test features file')
    parser.add_argument('--metric', default='rmse', type=str,
                        help='error metric (rmse, mae, etc)')
    parser.add_argument('--epochs', default=50, type=int,
                        help='number of Chemprop epochs to run with each observation')
    parser.add_argument('--name', default='peakwavs_max', type=str,
                        help='experiment name (target property)')
    parser.add_argument('--observation_budget', default=50, type=int,
                        help='number of observations to complete (must be at least 50 to get parameter importance for 10 parameters)')
    parser.add_argument('--save_dir', type=str, default='.',
                        help='directory to save `results` directory to')
    parser.add_argument('--solvation', action='store_true', default=False,
                        help='using 2 molecules instead of 1')
    parser.add_argument('--restart', type=str, default=None,
                        help='SigOpt experiment ID to restart if job failed')
    return parser

def main(args=None):
    # Command Line Argument Parsing
    parser = get_parser()
    args = parser.parse_args(args)

    # Connect with SigOpt API and run loop 
    # We follow a similar procedure to what is demonstrated here: https://app.sigopt.com/getstarted.
    sigopt_api_key = os.environ.get("SIGOPT_API_KEY") # private API key is stored in a local environment variable
    
    conn = Connection(client_token=sigopt_api_key)
    
    if args.restart:
        experiment = conn.experiments(args.restart).fetch()
        print("Restarting experiment: https://app.sigopt.com/experiment" + experiment.id)
        starting_observation_number = experiment.progress.observation_count
        print("Observations reported so far: ", starting_observation_number)
    else:
        experiment = conn.experiments().create(
          name=f'Chemprop {args.name}',
          project="fluodye",
          parameters=[
              dict(name='hidden_size', type='int', bounds=dict(min=300, max=2400)),
              dict(name='depth', type='int', bounds=dict(min=2, max=6)),
              dict(name='dropout', type='double', bounds=dict(min=0, max=0.4)),
              dict(name='ffn_num_layers', type='int', bounds=dict(min=1, max=3)),
              dict(name='ffn_hidden_size', type='int', bounds=dict(min=300, max=2400)),
              dict(name='warmup_epochs', type='int', bounds=dict(min=2, max=6)),
              dict(name='batch_size', type='int', bounds=dict(min=10, max=100)),
              dict(name='init_lr', type='double', bounds=dict(min=1e-3, max=1), transformation="log"),
              dict(name='max_lr', type='double', bounds=dict(min=1e-8, max=1e-3), transformation="log"),
              dict(name='final_lr', type='double', bounds=dict(min=1e-3, max=1), transformation="log"),
          ],
          metrics=[dict(name=args.metric, objective='minimize')],
          parallel_bandwidth=1,
          observation_budget=args.observation_budget,
        )
        print("Created experiment: https://app.sigopt.com/experiment/" + experiment.id)
        starting_observation_number = 0
    
    results_dir = os.path.join(args.save_dir,'results')

    if not os.path.exists(results_dir):
        os.mkdir(results_dir)
    
    experiment_dir = os.path.join(results_dir, experiment.id)
    if not os.path.exists(experiment_dir):
        os.mkdir(experiment_dir)

    # Run the Optimization Loop between 10x - 20x the number of parameters
    for i in range(starting_observation_number, experiment.observation_budget):
        suggestion = conn.experiments(experiment.id).suggestions().create()
        
        save_dir = os.path.join(results_dir,experiment.id,suggestion.id)
        os.mkdir(save_dir)
        
        print(f'Starting observation {i}')
        value = evaluate_chemprop_model(suggestion.assignments, save_dir, args)
        
        conn.experiments(experiment.id).observations().create(
            suggestion=suggestion.id,
            value=value,
        )

    # Fetch the best configuration and explore your experiment
    all_best_assignments = conn.experiments(experiment.id).best_assignments().fetch()
    # Returns a list of dict-like Observation objects
    best_assignments = all_best_assignments.data[0].assignments
    
    best_assignments['init_lr'] = best_assignments['init_lr']*best_assignments['max_lr']
    best_assignments['final_lr'] = best_assignments['final_lr']*best_assignments['max_lr']
    
    print("Best Assignments: " + str(best_assignments))
    print("Explore your experiment: https://app.sigopt.com/experiment/" + experiment.id + "/analysis")
    
    with open(f'sigopt_chemprop_{args.name}_best_hyperparams.json', 'w') as outfile:
        outfile.write(json.dumps(best_assignments.to_json(), indent=4))

if __name__ == '__main__':
    main()
