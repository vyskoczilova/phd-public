import glob
import os
import argparse
import pandas as pd

# Parametry
parser = argparse.ArgumentParser()
parser.add_argument('directory',
					help='Název složky (slovesa), ve které se budou brát stará oanotovaná data spojovat v jedno')
args = parser.parse_args()

# Načíst a spojit
all_files = glob.glob(os.path.join('./' + args.directory + '/old/*_anotovano.csv'))
df_from_each_file = (pd.read_csv(f, sep=";") for f in all_files)
df = pd.concat(df_from_each_file, ignore_index=True)

# Vyházet duplikáty pro jedno lemma a uložit do jednoho souboru
df.drop_duplicates(subset='lemma', inplace=True)
df.to_csv('./' + args.directory + '/old/anotovano.csv', index=False, sep=";")

# Source
# https://stackoverflow.com/questions/70560470/remove-duplicate-rows-of-a-csv-file-based-on-a-single-column
# https://stackoverflow.com/questions/20906474/import-multiple-csv-files-into-pandas-and-concatenate-into-one-dataframe

print('✅ Hotovo')
