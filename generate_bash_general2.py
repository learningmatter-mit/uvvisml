import re
import sys

#example: python3 generate_bash_general2.py same_test_set not
same_test_set = sys.argv[1:][0]
hyperparam_opt = sys.argv[1:][1]

opt_properties = ['lambda_max_abs', 'lambda_max_emi', 'both_peaks', 'abs_all', 'emi_all', 'multitask_peak_stats', 'multitask_all', 'quantum_yield', 'log_lifetime']
split_types = ['group_by_smiles', 'random', 'scaffold']
template = 'template.sh'
models_dir = 'uvvisml/models/'
python_str = 'python3 predict2.py '

if same_test_set == 'same_test_set':
    opt_properties = ['lambda_max_abs', 'lambda_max_emi', 'both_peaks']
    template = 'template_same_test_set.sh'
    models_dir = 'uvvisml/models_same_test_set/'
if hyperparam_opt == 'hyperparam_opt':
    template = '/home/kimele03/uvvisml/chemprop_sigopt_engaging.sh'
    models_dir = 'uvvisml/models/'
    python_str = 'python ../../chemprop_sigopt_engaging.py '    

fd = open(template, 'r')
output = fd.readlines()

for prop in opt_properties:
    for split in split_types:
        prop_split_name = prop + '_' + split
        prop_split_args = prop + ' ' + split

        checkpoints_dir = prop + '_checkpoints/'
        splits_dir = split + '/'
        file_name = models_dir + checkpoints_dir + splits_dir + prop_split_name
        if same_test_set == 'same_test_set':
            file_name += '_same_test_set'
        if hyperparam_opt == 'hyperparam_opt':
            file_name += '_hyperparam_opt'
            prop_split_args = '--data_path ../../../data/splits/lambda_max_abs/deep4chem/group_by_smiles/smiles_target_train.csv --separate_val_path ../../../data/splits/lambda_max_abs/deep4chem/group_by_smiles/smiles_target_val.csv --separate_test_path ../../../data/splits/lambda_max_abs/deep4chem/group_by_smiles/smiles_target_test.csv --metric rmse --epochs 50 --name ' + prop + ' --observation_budget 50 --save_dir $(pwd) --solvation'
        file_name += '.sh'

        fwd = open(file_name, 'w')

        for line in output:
            line = line.strip()
            if re.match('#SBATCH -J', line):
                if hyperparam_opt == 'hyperparam_opt':
                    result = '#SBATCH -J chemprop_sigopt_' + prop_split_name
                else:
                    result = re.sub(r"(#SBATCH -J) (.*)", r"\1 {}".format(prop_split_name), line)
                # print(result)
                fwd.write(result + '\n')
            elif re.match('#SBATCH -o', line):
                if hyperparam_opt == 'hyperparam_opt':
                    result = '#SBATCH -o chemprop_sigopt_' + prop_split_name + '-%j.out'
                else:
                    result = re.sub(r"(#SBATCH -o) (.*)", r"\1 {}-%j.out".format(prop_split_name), line)
                # print(result)
                fwd.write(result + '\n')
            elif re.match(python_str, line):
                result = re.sub(r"(python3 predict2.py) (.*)", r"\1 {}".format(prop_split_args), line)
                if same_test_set == 'same_test_set':
                    result += ' same_test_set'
                if hyperparam_opt == 'hyperparam_opt':
                    result = re.sub(r"(python ../../chemprop_sigopt_engaging.py) (.*)", r"\1 {}".format(prop_split_args), line)
                # print(result)
                fwd.write(result + '\n')
            else:
                # print(line)
                fwd.write(line + '\n')
            
        fwd.close()

fd.close()
