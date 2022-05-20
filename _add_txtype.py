import argparse
import os
import re

import pandas as pd
from scripts.helpers import Helpers
from scripts.concordance import ConcordanceRow

# Parametry
parser = argparse.ArgumentParser()
parser.add_argument('directory', help='Název složky (slovesa), ve které se budou doplňovat informace')
args = parser.parse_args()

# Zjisti jestli složka existuje
parent_directory = './' + args.directory + '/'
if not os.path.isdir(parent_directory):
	print("Adresář neexistuje.")
	quit()

# Získej seznam souborů pro doplnění
files_to_update = Helpers.get_list_of_annotated_files(parent_directory)

# Načti zdroj
file_txtype = Helpers.csv_file_starts_with(parent_directory, 'txtype_kontext-conc')
df_txtype = pd.read_csv(parent_directory + file_txtype, sep=";", index_col=0, dtype=str, keep_default_na=False)
df_txtype = df_txtype.reset_index()


def has_same_txtype(df_found):
	unique = df_found['doc.txtype_group'].unique()
	if len(unique) == 1:
		return unique[0]
	return False


# Projdi jednotlivé soubory a vytáhni si data
breaker = 0
for file in files_to_update:
	df = pd.read_csv(file, sep=";", index_col=0, dtype=str, keep_default_na=False)
	df = df.reset_index()
	txtype_values = []

	if "doc.txtype_group" not in df.columns:
		if breaker > -1:
			for index, row in df.iterrows():
				df_found_kwic = df_txtype[df_txtype['kwic'].isin([row["kwic"]])]  # exact match
				txtype = has_same_txtype(df_found_kwic)

				if len(df_found_kwic) == 0:
					txtype = "TODO empty"

				if not txtype:
					df_found = df_found_kwic[df_found_kwic['right'].isin([row["right"]])]  # exact match
					txtype = has_same_txtype(df_found)

					if not txtype:
						df_found = df_found[df_found['left'].isin([row["left"]])]  # exact match
						txtype = has_same_txtype(df_found)

						if not txtype:
							# df_found = df_found_kwic.filter(like=row["left"], axis=0)  # find string in string
							df_found = df_found_kwic[
								df_found_kwic['left'].str.contains(re.escape(row["left"]))]  # find string in string
							# print()
							# print(df_found_kwic)
							# print(df_found)
							# print(row["left"])

							txtype = has_same_txtype(df_found)

							if not txtype:
								# df_found = df_found_kwic.filter(like=row["right"], axis=0)  # find string in string
								if len(df_found):
									df_found = df_found[df_found['right'].str.contains(
										re.escape(row["right"]))]  # find string in string
								else:
									df_found = df_found_kwic[df_found_kwic['right'].str.contains(
										re.escape(row["right"]))]  # find string in string
								txtype = has_same_txtype(df_found)

								if not txtype:
									txtype = "TODO"
									print("TODO - " + file)
				txtype_values.append(txtype)
			df["doc.txtype_group"] = txtype_values
			df.to_csv(file, sep=";", encoding="utf-8", index=False)
			print('✅ uloženo')
			breaker += 1
