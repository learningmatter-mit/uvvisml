
# coding: utf-8

# # Imports

# In[1]:


import pandas as pd
import os
import numpy as np
from rdkit.Chem import AllChem as Chem
import sys
sys.path.append('..')


# In[2]:


WORK_DIR = os.getcwd()

DATA_DIR = os.path.join(WORK_DIR,'original')

data_processed_dir = os.path.join(WORK_DIR,'processed')
if not os.path.exists(data_processed_dir):
    os.makedirs(data_processed_dir)


# # Read Raw Data

# Read the raw data files, rename columns, drop NaN and extraneous information

# ### ChemFluor

# In[3]:


data_location = os.path.join(DATA_DIR, 'chem_fluor/Alldata_SMILES.xlsx')
chemfluor_df = pd.read_excel(data_location)
chemfluor_df.rename(columns={'SMILES':'smiles',"Absorption/nm":'peakwavs_max'}, inplace=True)
chemfluor_df = chemfluor_df[['smiles','solvent','peakwavs_max']].copy()
chemfluor_df.dropna(inplace=True)
chemfluor_df['source'] = 'chemfluor'
chemfluor_df


# ### DSSCDB

# In[4]:


data_location = os.path.join(DATA_DIR, 'dsscdb')
xlsx_files = [x for x in os.listdir(data_location) if x.endswith('.xlsx')]
dsscdb_df = pd.DataFrame()
for file in xlsx_files:
    file_location = os.path.join(data_location, file)
    dsscdb_df = dsscdb_df.append(pd.read_excel(file_location), ignore_index=True, sort=True)

dsscdb_df.rename(columns={'SMILES':'smiles','SOLVENT':'solvent','ABSORPTION_MAXIMA':'peakwavs_max'}, inplace=True)
dsscdb_df = dsscdb_df[['smiles','solvent','peakwavs_max']].copy()
dsscdb_df.dropna(inplace=True)
dsscdb_df['source'] = 'dsscdb'
dsscdb_df


# ### DyeAgg

# In[5]:


data_location = os.path.join(DATA_DIR, 'dye_agg/new_dssc_Search_results.csv')
dyeagg_df = pd.read_csv(data_location, sep=';')
dyeagg_df.rename(columns={'STRUCTURE':'smiles','SOLVENT':'solvent','PEAK_ABSORPTION_SOLUTION':'peakwavs_max'}, 
                 inplace=True)
dyeagg_df = dyeagg_df[['smiles','solvent','peakwavs_max']].copy()
dyeagg_df.dropna(inplace=True)
dyeagg_df['source'] = 'dyeagg'
dyeagg_df


# ### CDEx

# In[6]:


data_location = os.path.join(DATA_DIR, 'jcole/paper_allDB.csv')
jcole_df = pd.read_csv(data_location)
jcole_df.rename(columns={'SMI':'smiles', "lambda_max (Exp,  nm)": 'peakwavs_max'}, inplace=True)
jcole_df = jcole_df[['smiles','solvent','peakwavs_max']].copy()
jcole_df.dropna(inplace=True)
jcole_df['source'] = 'cdex'
jcole_df


# ### Deep4Chem

# In[7]:


data_location = os.path.join(DATA_DIR, 'joung/DB_for_chromophore_Sci_Data_rev02.csv')
joung_df = pd.read_csv(data_location)

joung_df.rename(columns={'Chromophore':'smiles','Solvent':'solvent', 'Absorption max (nm)':'peakwavs_max'}, 
                inplace=True)

# Drop measurements where solvent == 'gas'
gas_idx = joung_df[joung_df['solvent']=='gas'].index
joung_df.drop(index=gas_idx, inplace=True)

# Drop measurements taken in solid state (original authors wrote file as chromophore == solvent for these cases)
ss_idx = joung_df[joung_df['smiles']==joung_df['solvent']].index
joung_df.drop(index=ss_idx, inplace=True)

joung_df = joung_df[['smiles','solvent','peakwavs_max']].copy()
joung_df.dropna(inplace=True)
joung_df['source'] = 'deep4chem'

joung_df


# # Convert Solvent Names to SMILES

# In[8]:


no_solvent_smiles_df = pd.concat([chemfluor_df, dsscdb_df, dyeagg_df, jcole_df])
no_solvent_smiles_df.reset_index(drop=True, inplace=True)
no_solvent_smiles_df['solvent'] = no_solvent_smiles_df['solvent'].apply(lambda x: x.lower().strip())
no_solvent_smiles_df


# In[9]:


# Exclude all solvents that are ionic, mixtures, polymers, or not clear what they are

bad_solvents = ['-','n','10 − 4–10 − 6 m','quartz','silica','pbs','pvc','ch3cn-ch2cl2','acetonitrile + tert-butanol',
                'cl','poly(ethylene glycol)s','chcl','methanol, tert-butyl alcohol-acetonitrile',
                'methanol-chloroform','tbaf','chcl3-ch3oh','ch 2 cl 2 + 0.2 mmol l − 1 bu 4 nbf','ch3oh–h2o','pmma',
                'ch3oh+chcl3','t-buoh-an','ni','ch 2 cl','acetonitrile-dmso','acetonitrile and tert-butyl alcohol',
                'sds','tert-butanol–acetonitrile','chcl3–ch3oh','barium sulfate','mecn-dcm','chloroform + methanol',
                'ch3oh-chcl3','kbr','2-methyl-2-propanol-acetonitrile']
no_solvent_smiles_df = no_solvent_smiles_df.loc[~no_solvent_smiles_df['solvent'].isin(bad_solvents)]

for bad_symbol in ['%','/',':']:
    no_solvent_smiles_df = no_solvent_smiles_df.loc[~no_solvent_smiles_df['solvent'].str.contains(bad_symbol)]
    
no_solvent_smiles_df


# In[10]:


# Dictionary for standardizing abbreviations and different names for the same solvents
replace_solvents_master_dict = {'acn':'acetonitrile', 'c6h6':'benzene', 'c6h12':'cyclohexane', 
                                'ccl4':'carbon tetrachloride', 'ch2cl2':'dichloromethane', 
                                'ch 2 cl 2':'dichloromethane','ch3cn':'acetonitrile', 
                                'ch 3 cn':'acetonitrile','ch 3 oh':'methanol', 'chcl3':'chloroform', 
                                'chroroform':'chloroform',
                                'chx':'chlorohexidine',
                                'ctc':'carbon tetrachloride', 
                                'dichloromethane.':'dichloromethane','dcb':'1,2-dichlorobenzene', 
                                'dcm':'dichloromethane', 
                                'dee': 'diethyl ether',
                                'dimethylsulfoxide':'dmso', 'dimethylsufoxide':'dmso', 'dimethyl sulfoxide':'dmso', 
                                'dma':'dimethylacetamide', 'dmf':'dimethylformamide', 
                                'ethylacetate': 'ethyl acetate', 'etoh':'ethanol', 
                                'etoac':'ethyl acetate', 'h 2 o':'water', 'h2o':'water', 'hcl':'hydrochloric acid', 
                                'hex':'hexane',
                                'mch': 'methylcyclohexane',
                                'mecn':'acetonitrile', 'meoh':'methanol', 
                                'me-thf':'2-methyltetrahydrofuran', 'mthf':'2-methyltetrahydrofuran', 
                                'nmp':'n-methyl-2-pyrrolidone','o-c6h4cl2': 'orthodichlorobenzene',
                                'pgmea':'propylene glycol methyl ether acetate',
                                'phcl':'chlorobenzene',
                                'phcn':'benzonitrile',
                                'tfa':'trifluoroacetic acid', 'tfe':'2,2,2-trifluoroethanol', 
                                'thf':'tetrahydrofuran', 'toluol':'toluene'}

# Dictionary for replacing all full solvent names with solvent SMILES
solvent_smiles_dict = {'cyclohexane': 'C1CCCCC1', 'dmso': 'CS(=O)C','ethylene glycol': 'C(CO)O',
                        'ethanol': 'CCO','methanol': 'CO','dioxane': 'C1COCCO1','pyridine': 'c1ccncc1',
                        'chlorobenzene': 'Clc1ccccc1','water': 'O','glycerin': 'OCC(O)CO',
                        'dichloromethane': 'ClCCl','carbon tetrachloride': 'ClC(Cl)(Cl)Cl',
                        'toluene': 'Cc1ccccc1','chloronaphthalene': 'Clc1cccc2ccccc12','hexane': 'CCCCCC',
                        'acetonitrile': 'CC#N','chloroform': 'ClC(Cl)Cl','benzene': 'c1ccccc1',
                        'dimethylformamide': 'CN(C)C=O','tetrahydrofuran': 'C1CCOC1',
                        'triethylamine': 'CCN(CC)CC','bromobenzene': 'Brc1ccccc1',
                        '2-methylbutane': 'CCC(C)C','2-pentanone': 'CCCC(C)=O',
                        'di-n-butyl ether': 'CCCCOCCCC','glycerol': 'OCC(O)CO','methyl formate': 'COC=O',
                        '2-propanol': 'CC(C)O','diisopropyl ether': 'CC(C)OC(C)C','1-octanol': 'CCCCCCCCO',
                        '2,2,2-trifluoroethanol': 'OCC(F)(F)F','2-methyltetrahydrofuran': 'CC1CCCO1',
                        'methylcyclohexane': 'CC1CCCCC1','1-butanol': 'CCCCO','heptane': 'CCCCCCC',
                        'ethyl acetate': 'CCOC(C)=O','1,2-dichlorobenzene': 'Clc1ccccc1Cl',
                        '1-decanol': 'CCCCCCCCCCO','formamide': 'NC=O','acetone': 'CC(C)=O',
                        'dimethylacetamide': 'CN(C)C(C)=O','o-dimethoxybenzene': 'COc1ccccc1OC',
                        'n-methylformamide': 'CNC=O','diethyl ether': 'CCOCC','1-hexanol': 'CCCCCCO',
                        '1-methyl-2-pyrrolidinone': 'CN1CCCC1=O','butyl acetate': 'CCCCOC(C)=O',
                        'tert-pentanol': 'CCC(C)(C)O','2-methyl-2-propanol': 'CC(C)(C)O',
                        '1,2-propanediol': 'CC(O)CO','1-propanol': 'CCCO','methyl acetate': 'COC(C)=O',
                        'trifluoroacetic acid': 'OC(=O)C(F)(F)F',
                        'n-methyl-2-pyrrolidone': 'CN1CCCC1=O', '1,4-dioxane': 'C1COCCO1',
                        'hydrochloric acid': 'Cl', 'benzonitrile': 'N#Cc1ccccc1',
                        'propanol': 'CCCO', 'propylene carbonate': 'CC1COC(=O)O1',
                        'benzyl alcohol': 'OCc1ccccc1', 'butanol': 'CCCCO',
                        'propylene glycol methyl ether acetate': 'COCC(C)OC(C)=O', 'isopropanol': 'CC(C)O',
                        'methylene chloride': 'ClCCl', 'n-hexane': 'CCCCCC',
                        'octene': 'CCCCCCC=C', 'mops': 'O[S](=O)(=O)CCCN1CCOCC1',
                        'tetrachloromethane': 'ClC(Cl)(Cl)Cl', 'pentane': 'CCCCC',
                        'chlorobenzene': 'Clc1ccccc1', 'acetic acid': 'CC(O)=O', '1,2-dichloroethane': 'ClCCCl',
                       'chlorohexidine':'Clc1ccc(NC(=N)NC(=N)NCCCCCCNC(=N)NC(=N)Nc2ccc(Cl)cc2)cc1',
                       'orthodichlorobenzene':'C1=CC=C(C(=C1)Cl)Cl', 'tert-butyl alcohol':'CC(C)(C)O',
               }

solvents_set = set(no_solvent_smiles_df['solvent'])
#print(len(solvents_set))

solvents_for_df_dict = {}
for solvent in solvents_set:
    if solvent in replace_solvents_master_dict.keys():
        solvent_ = replace_solvents_master_dict[solvent]
    else:
        solvent_ = solvent
    solvents_for_df_dict[solvent] = solvent_smiles_dict[solvent_]


# In[11]:


# Replace names with SMILES
no_solvent_smiles_df['solvent'] = no_solvent_smiles_df['solvent'].map(solvents_for_df_dict)
no_solvent_smiles_df


# # Combine All Sources

# In[12]:


df = pd.concat([no_solvent_smiles_df, joung_df])
df = df.loc[df['peakwavs_max']!='-'].copy()
df['peakwavs_max'] = df['peakwavs_max'].apply(lambda x: float(x))
df


# # Filtering

# ### Remove Molecules that Cannot be Sanitized by RDKit

# In[13]:


def sanitize_smiles(smiles):
    try:
        smiles = Chem.MolToSmiles(Chem.MolFromSmiles(smiles))
    except:
        smiles = np.nan
    return smiles

df['smiles'] = df['smiles'].apply(lambda x: sanitize_smiles(x))
df['solvent'] = df['solvent'].apply(lambda x: sanitize_smiles(x))
df.dropna(inplace=True)
df


# ### Remove Clusters (SMILES containing ".")

# In[14]:


cluster_idx = df[df['smiles'].str.contains('\.')].index
#print('Removing {} rows'.format(len(cluster_idx)))
df.drop(index=cluster_idx, inplace=True)
df


# # Export DataFrame to CSV File

# In[15]:


df[['smiles','solvent','peakwavs_max','source']].to_csv(f'{data_processed_dir}/all_lambda_max_abs_including_duplicates.csv', 
                                                        index=False)


# # Stats

# ### Table 2

# In[16]:


df['source'].value_counts()


# In[17]:


df.drop_duplicates(subset=['smiles','solvent'])


# In[18]:


df.groupby(['smiles','solvent']).count().query('source > 1')


# In[19]:


len(set(df['smiles']))


# In[20]:


len(set(df['solvent']))


# ### Table S1

# In[21]:


dict(df['solvent'].value_counts())

