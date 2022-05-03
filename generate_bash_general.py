import re
import sys

same_test_set = sys.argv[1:][0]
hyperparam_opt = sys.argv[1:][1]

opt_properties = ['lambda_max_abs', 'lambda_max_emi', 'both_peaks', 'abs_all', 'emi_all', 'multitask_peak_stats', 'multitask_all', 'quantum_yield', 'log_lifetime']
split_types = ['group_by_smiles', 'random', 'scaffold']
template = 'template.sh'
batch_scripts_dir = 'batch_scripts/'
python_str = 'python3 predict2.py '

if same_test_set == 'same_test_set':
    opt_properties = ['lambda_max_abs', 'lambda_max_emi', 'both_peaks']
    template = 'template_same_test_set.sh'
    batch_scripts_dir = 'batch_scripts_same_test_set/'
if hyperparam_opt == 'hyperparam_opt':
    template = '/home/kimele03/uvvisml/chemprop_sigopt_engaging.sh'
    batch_scripts_dir = 'batch_scripts_hyperparam_opt/'
    python_str = 'python chemprop_sigopt_engaging.py '    

fd = open(template, 'r')
output = fd.readlines()

for prop in opt_properties:
    for split in split_types:
        prop_split_name = prop + '_' + split
        prop_split_args = prop + ' ' + split
        if hyperparam_opt == 'hyperparam_opt':
            prop_split_args = '--data_path smiles_target_test.csv --separate_val_path smiles_target_val.csv --separate_test_path smiles_target_test.csv --metric rmse --name ' + prop + ' --observation_budget 50 --save_dir $(pwd)'

        file_name = batch_scripts_dir + prop_split_name + '.sh'
        
        fwd = open(file_name, 'w')

        for line in output:
            line = line.strip()
            if re.match('#SBATCH -J', line):
                result = re.sub(r"(#SBATCH -J) (.*)", r"\1 {}".format(prop_split_name), line)
                # print(result)
                fwd.write(result + '\n')
            elif re.match('#SBATCH -o', line):
                result = re.sub(r"(#SBATCH -o) (.*)", r"\1 {}-%j.out".format(prop_split_name), line)
                # print(result)
                fwd.write(result + '\n')
            elif re.match(python_str, line):
                result = re.sub(r"(python3 predict2.py) (.*)", r"\1 {}".format(prop_split_args), line)
                if same_test_set == 'same_test_set':
                    result += ' same_test_set'
                if hyperparam_opt == 'hyperparam_opt':
                    result = re.sub(r"(python chemprop_sigopt_engaging.py) (.*)", r"\1 {}".format(prop_split_args), line)
                # print(result)
                fwd.write(result + '\n')
            else:
                # print(line)
                fwd.write(line + '\n')
            
        fwd.close()

fd.close()
