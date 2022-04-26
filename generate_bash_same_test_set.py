import re

opt_properties = ['lambda_max_abs', 'lambda_max_emi', 'both_peaks']
split_types = ['group_by_smiles', 'random', 'scaffold']

template = 'template_same_test_set.sh'
fd = open(template, 'r')
output = fd.readlines()

for prop in opt_properties:
    for split in split_types:
        prop_split_name = prop + '_' + split
        prop_split_args = prop + ' ' + split

        file_name = 'batch_scripts_same_test_set/'+ prop_split_name + '.sh'
        
        fwd = open(file_name, 'w')

        for line in output:
            line = line.strip()
            if re.match('#SBATCH -J', line):
                result = re.sub(r"(#SBATCH -J) (.*)", r"\1 {}".format(prop_split_name), line)
                #print(result)
                fwd.write(result + '\n')
            elif re.match('#SBATCH -o', line):
                result = re.sub(r"(#SBATCH -o) (.*)", r"\1 {}-%j.out".format(prop_split_name), line)
                #print(result)
                fwd.write(result + '\n')
            elif re.match('python3 predict2.py ', line):
                result = re.sub(r"(python3 predict2.py) (.*)", r"\1 {}".format(prop_split_args), line) + ' same_test_set'
                #print(result)
                fwd.write(result + '\n')
            else:
                #print(line)
                fwd.write(line + '\n')
            
        fwd.close()

fd.close()
