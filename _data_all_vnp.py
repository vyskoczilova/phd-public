import argparse
import os
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

# Získej seznam souborů
files_to_update = Helpers.get_list_of_annotated_files(parent_directory)

data = []
data_non_vnp = []
columns = ["podstatné jmeno", "typ", "anotovano", "left", "kwic", "right", "kwic pos", "kwic pos2", "kwic pos2 full",
		   "kwic length"]
columns_non_vnp = ["podstatné jmeno", "typ", "left", "kwic", "right", "kwic pos", "kwic pos2", "kwic length"]

# Projdi jednotlivé soubory a vytáhni si data
for file in files_to_update:
	df = pd.read_csv(file, sep=";", index_col=0, dtype=str, keep_default_na=False)
	df = df.reset_index()

	noun = file.split("/").pop(-2)
	cql_type = file.split("/").pop()[0:3]

	for index, row in df.iterrows():

		c_row = ConcordanceRow(row["left"], row["kwic"], row["right"])

		pos = c_row.kwic_get_pos()
		pos_formatted = c_row.kwic_get_pos_formatted()
		pos_detailed_formatted_simplified = c_row.kwic_get_pos_detailed_formatted_simplified()

		if row["VNP?"] != "0":
			data_row = [noun, cql_type, row["VNP?"]]

			data_row.append(c_row.strip_lemma_and_tag('left'))
			data_row.append(c_row.strip_lemma_and_tag('kwic'))
			data_row.append(c_row.strip_lemma_and_tag('right'))

			data_row.append(pos_formatted)
			data_row.append(pos_detailed_formatted_simplified)
			data_row.append(c_row.kwic_get_pos_detailed_formatted())
			data_row.append(len(pos))

			data.append(data_row)

		else:
			data_row = [noun, cql_type]

			c_row = ConcordanceRow(row["left"], row["kwic"], row["right"])

			data_row.append(c_row.strip_lemma_and_tag('left'))
			data_row.append(c_row.strip_lemma_and_tag('kwic'))
			data_row.append(c_row.strip_lemma_and_tag('right'))
			data_row.append(pos_formatted)
			data_row.append(pos_detailed_formatted_simplified)
			data_row.append(len(pos))

			data_non_vnp.append(data_row)

# Create the pandas DataFrame
df_vnp = pd.DataFrame(data, columns=columns)
df_non_vnp = pd.DataFrame(data_non_vnp, columns=columns_non_vnp)
print(df_vnp)

# Filter 80 % VNPs structures
# TODO update manually!!!!
structures = ["V-N", "V-A-N", "N-V", "V-P-N", "V-R-P-A-N", "V-D-A-N", "V-R-P-N", "V-R-N-A-N", "V-R-N-N", "N-R-P-V",
			  "V-P-A-N", "V-N-J-N", "V-A-N-J-N", "V-R-P-N-A-N", "N-R-N-V", "V-R-A-N-A-N", "V-D-N", "V-T-A-N", "V-A-A-N",
			  "V-R-N-P-N", "V-R-P-N-N", "V-R-N-N-N", "V-A-J-A-N", "V-R-P-P-N", "V-R-A-N-N", "N-R-A-N-V"]

df_vnp_filtered = df_vnp.loc[df_vnp["kwic pos"].isin(structures)]
df_non_vnp_filtered = df_non_vnp.loc[df_non_vnp["kwic pos"].isin(structures)]

# Ulož csv
print()
df_vnp.to_csv(parent_directory + '/_data/all_vnp.csv', sep=";", encoding="utf-8", index=False)
df_non_vnp.to_csv(parent_directory + '/_data/all_rest.csv', sep=";", encoding="utf-8", index=False)
print('✅ CSV uloženo')

# Create a Pandas Excel writer using XlsxWriter as the engine.
# https://xlsxwriter.readthedocs.io/example_pandas_multiple.html
writer = pd.ExcelWriter(parent_directory + '/_data/all.xlsx', engine='xlsxwriter')

# Write each dataframe to a different worksheet.
df_vnp.to_excel(writer, sheet_name='VNP + vztažné')
df_non_vnp.to_excel(writer, sheet_name='ostatní')
df_vnp_filtered.to_excel(writer, sheet_name='80% VNP + vztažné')
df_non_vnp_filtered.to_excel(writer, sheet_name='80% ostatní')

# Close the Pandas Excel writer and output the Excel file.
writer.save()

print('✅ Excel uložen')
