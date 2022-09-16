import argparse
import os
import pandas as pd
from scripts.helpers import Helpers, prcnt_wrap, prcnt
from scripts.concordance import ConcordanceRow

# Parameters
parser = argparse.ArgumentParser()
parser.add_argument('directory', help='Název složky (slovesa), ve které se budou doplňovat informace')
args = parser.parse_args()

# Check if directory exists
parent_directory = './' + args.directory + '/'
if not os.path.isdir(parent_directory):
	print("Adresář neexistuje.")
	quit()

# Získej seznam souborů
files_to_update = Helpers.get_list_of_annotated_files(parent_directory)

data = []
data_non_vnp = []
data_noun_number = {"P": 0, "S": 0, "Plemmas": {}, "Slemmas": {}}
columns = ["podstatné jmeno", "typ", "anotovano", "left", "kwic", "right", "kwic pos", "kwic pos2", "kwic pos2 plné",
		   "kwic délka"]
columns_non_vnp = ["podstatné jmeno", "typ", "left", "kwic", "right", "kwic pos", "kwic pos2", "kwic délka"]

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

			# Count noun number (singular/plural)
			noun_number = c_row.get_nouns_number()
			data_noun_number[noun_number] += 1
			if not noun in data_noun_number[noun_number + "lemmas"].keys():
				data_noun_number[noun_number + "lemmas"][noun] = 0
			data_noun_number[noun_number + "lemmas"][noun] += 1

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

# Noun number results
print()
print("ℹ Číslo predikativního jména")
print("singular : " + str(data_noun_number["S"]) + " " + prcnt_wrap(data_noun_number["S"],
																	data_noun_number["S"] + data_noun_number["P"],
																	after=" %)"))
print("plurál: " + str(data_noun_number["P"]) + " " + prcnt_wrap(data_noun_number["P"],
																 data_noun_number["S"] + data_noun_number["P"],
																 after=" %)"))

# Singular:
# {'předsudek': 1, 'potřeba': 3, 'názor': 6, 'plán': 7, 'záměr': 8, 'ambice': 9, 'iluze': 10, 'obava': 10, 'antipatie': 11, 'obraz': 11, 'slabost': 14, 'úmysl': 16, 'přání': 18, 'zloba': 18, 'sympatie': 19, 'myšlenka': 21, 'nevraživost': 22, 'nechuť': 23, 'postoj': 23, 'despekt': 25, 'opovržení': 28, 'sen': 28, 'pocit': 32, 'přízeň': 33, 'skepse': 34, 'představa': 36, 'přátelství': 42, 'vášeň': 42, 'přesvědčení': 43, 'touha': 43, 'víra': 57, 'nepřátelství': 59, 'cit': 95, 'odpor': 122, 'podezření': 185, 'vztah': 252, 'náklonnost': 256, 'nedůvěra': 263, 'nenávist': 308, 'důvěra': 316, 'zášť': 334, 'láska': 369, 'obdiv': 412, 'naděje': 579, 'respekt': 1218, 'úcta': 1396}
# Plural:
# {'náklonnost': 1, 'víra': 1, 'zloba': 2, 'nenávist': 3, 'obraz': 3, 'plán': 3, 'přesvědčení': 4, 'přání': 4, 'láska': 5, 'ohled': 5, 'úcta': 5, 'touha': 7, 'sen': 8, 'záměr': 8, 'názor': 12, 'postoj': 12, 'podezření': 16, 'myšlenka': 23, 'představa': 33, 'ambice': 35, 'úmysl': 35, 'obava': 39, 'antipatie': 43, 'iluze': 48, 'vztah': 49, 'předsudek': 51, 'naděje': 101, 'pocit': 142, 'sympatie': 630, 'cit': 632}

data_numbers_columns = ["lemma", "plural %", "singulár (%)", "plurál (%)", "celkem"]
data_numbers_rows = []

for key, plural in data_noun_number["Plemmas"].items():
	singular = data_noun_number["Slemmas"][key] if key in data_noun_number["Slemmas"].keys() else 0
	total = singular + plural
	data_numbers_rows.append([
		key,
		prcnt(plural, total),
		str(singular) + " " + prcnt_wrap(singular, total),
		str(plural) + " " + prcnt_wrap(plural, total),
		str(total)
	])
for key, singular in data_noun_number["Slemmas"].items():
	if key not in data_noun_number["Plemmas"].keys():
		plural = 0
		total = singular + plural
		data_numbers_rows.append([
			key,
			prcnt(plural, total),
			str(singular) + " " + prcnt_wrap(singular, total),
			str(plural) + " " + prcnt_wrap(plural, total),
			str(total)
		])

df_numbers = pd.DataFrame(data_numbers_rows, columns=data_numbers_columns)
df_numbers = df_numbers.sort_values(by=["plural %"], ascending=False)
df_numbers = df_numbers.drop(columns=["plural %"])

# Create the pandas DataFrame
df_vnp = pd.DataFrame(data, columns=columns)
df_non_vnp = pd.DataFrame(data_non_vnp, columns=columns_non_vnp)

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
df_vnp.to_excel(writer, sheet_name='APKS + vztažné')
df_non_vnp.to_excel(writer, sheet_name='ostatní')
df_vnp_filtered.to_excel(writer, sheet_name='80 % APKS + vztažné')
df_non_vnp_filtered.to_excel(writer, sheet_name='80 % ostatní')
df_numbers.to_excel(writer, sheet_name='Číslo pred. jm.')

# Close the Pandas Excel writer and output the Excel file.
writer.save()

print('✅ Excel uložen')
