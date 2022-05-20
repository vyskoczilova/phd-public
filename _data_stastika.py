import argparse
import os
import pandas as pd
from scripts.helpers import Helpers
from scripts.collocations import Collocations
from scripts.data import DataLemmas, DataTypes
import locale

from scripts.word_lists import WordLists

locale.setlocale(locale.LC_ALL, "cs_CZ.UTF-8")

# Parametry
parser = argparse.ArgumentParser()
parser.add_argument('directory', help='Název složky (slovesa), ve které se budou doplňovat informace')
args = parser.parse_args()

# Zjisti jestli složka existuje
parent_directory = './' + args.directory + '/'
if not os.path.isdir(parent_directory):
	print("Adresář neexistuje.")
	quit()

# Načíst už schválené VNP
accepted_vnps = WordLists()
accepted_vnps.loadWordList(parent_directory + "vallex_unique.txt", "VALLEX")
accepted_vnps.loadWordList(parent_directory + "radimsky.txt", "Radimský")
accepted_vnps.loadWordList(parent_directory + "vallex_working_unique.txt", "VALLEX - working")

# Získej seznam souborů
files_to_update = Helpers.get_list_of_annotated_files(parent_directory)

# Collocations
collocations = Collocations(parent_directory)

# Projdi jednotlivé soubory a vytáhni si data

# Data jednotlivě po lemmatech a typech
data = []
for file in files_to_update:
	df = pd.read_csv(file, sep=";", index_col=0, dtype=str, keep_default_na=False)
	df = df.reset_index()

	noun = file.split("/").pop(-2)
	cql_type = file.split("/").pop()[0:3]

	data_item = DataLemmas(noun, cql_type)
	data_item.setTotal(df.shape[0])

	if accepted_vnps.search(noun):
		data_item.setAcceptedAlready()

	for index, row in df.iterrows():
		if row["VNP?"] == '0':
			data_item.add("ostatni")
		elif row["VNP?"] == '1':
			data_item.add("vnp")
			data_item.addWordcount(len(row["kwic"].split()))
		elif row["VNP?"] == '3':
			data_item.add("vztazne")
		else:
			data_item.add("neurceno")
	data.append(data_item)

# Data po typech
data_nv = []
data_vn = []
data_summary_nv = DataTypes("N-V")
data_summary_vn = DataTypes("V-N")
data_summary_celkem = DataTypes("celkem")

for item in data:
	data_summary_celkem.add("vnp", item.getCounts("vnp"))
	data_summary_celkem.add("vztazne", item.getCounts("vztazne"))
	data_summary_celkem.add("ostatni", item.getCounts("ostatni"))
	if item.getType() == 'N-V':
		data_nv.append(item)
		data_summary_nv.add("vnp", item.getCounts("vnp"))
		data_summary_nv.add("vztazne", item.getCounts("vztazne"))
		data_summary_nv.add("ostatni", item.getCounts("ostatni"))
		data_summary_nv.addWordCounts(item.getWordcounts())
	else:
		data_vn.append(item)
		data_summary_vn.add("vnp", item.getCounts("vnp"))
		data_summary_vn.add("ostatni", item.getCounts("ostatni"))
		data_summary_vn.addWordCounts(item.getWordcounts())

# Basic DataFrame
basic_columns = ["lemma", "typ", "celkem", "neurčeno", "ostaní", "vztažné", "vztažné %", "VNP", "VNP %",
				 "VNP + vztažné %", "max. počet slov", "průměr", "modus"]
basic_rows = []
for item in data:
	basic_rows.append(
		[item.lemma, item.getType(), item.getTotal(), item.getCounts("neurceno"), item.getCounts("ostatni"),
		 item.getCounts("vztazne"), item.getPercentage("vztazne"), item.getCounts("vnp"), item.getPercentage("vnp"),
		 item.getPercentage("vnp") + item.getPercentage("vztazne"), item.getWordcountsMax(), item.getWordcountsMean(),
		 item.getWordcountsMode()])
df_basic = pd.DataFrame(basic_rows, columns=basic_columns)

# Summary DataFrame
summary_columns = ["typ", "VNP", "VNP %", "vztažné", "vztažné %", "ostatní", "ostatní %", "celkem", "celkem %"]
summary_rows = [
	["N-V", data_summary_nv.getCounts("vnp"), data_summary_nv.getPercentage("vnp"),
	 data_summary_nv.getCounts("vztazne"), data_summary_nv.getPercentage("vztazne"),
	 data_summary_nv.getCounts("ostatni"), data_summary_nv.getPercentage("ostatni"), data_summary_nv.getTotal(),
	 data_summary_nv.getTotalPercentage(data_summary_celkem.getTotal())],
	["V-N", data_summary_vn.getCounts("vnp"), data_summary_vn.getPercentage("vnp"), 0, 0,
	 data_summary_vn.getCounts("ostatni"), data_summary_vn.getPercentage("ostatni"), data_summary_vn.getTotal(),
	 data_summary_vn.getTotalPercentage(data_summary_celkem.getTotal())],
	["celkem", data_summary_celkem.getCounts("vnp"), data_summary_celkem.getPercentage("vnp"),
	 data_summary_celkem.getCounts("vztazne"), data_summary_celkem.getPercentage("vztazne"),
	 data_summary_celkem.getCounts("ostatni"), data_summary_celkem.getPercentage("ostatni"),
	 data_summary_celkem.getTotal(), 100],
]
df_summary = pd.DataFrame(summary_rows, columns=summary_columns)

# Summary cite DataFrame
summary_cite_columns = ["typ", "VNP (%)", "vztažné (%)", "ostatní (%)", "celkem (%)"]
summary_cite_rows = [
	["N-V", data_summary_nv.getCountsWithPercentage("vnp"), data_summary_nv.getCountsWithPercentage("vztazne"),
	 data_summary_nv.getCountsWithPercentage("ostatni"),
	 data_summary_nv.getTotalWithPercentage(data_summary_celkem.getTotal())],
	["V-N", data_summary_vn.getCountsWithPercentage("vnp"), "0 (0)",
	 data_summary_vn.getCountsWithPercentage("ostatni"),
	 data_summary_vn.getTotalWithPercentage(data_summary_celkem.getTotal())],
	["celkem", data_summary_celkem.getCountsWithPercentage("vnp"),
	 data_summary_celkem.getCountsWithPercentage("vztazne"),
	 data_summary_celkem.getCountsWithPercentage("ostatni"),
	 data_summary_celkem.getTotalWithPercentage(data_summary_celkem.getTotal())],
]
df_summary_cite = pd.DataFrame(summary_cite_rows, columns=summary_cite_columns)
print()
print(df_summary_cite)

# Distance DataFrame
distance_columns = ["typ", "min.", "max.", "průměr", "modus"]
distance_rows = [
	[
		"N-V",
		data_summary_nv.getWordcountsMin(),
		data_summary_nv.getWordcountsMax(),
		data_summary_nv.getWordcountsMean(),
		data_summary_nv.getWordcountsMode(),
	],
	[
		"V-N",
		data_summary_vn.getWordcountsMin(),
		data_summary_vn.getWordcountsMax(),
		data_summary_vn.getWordcountsMean(),
		data_summary_vn.getWordcountsMode(),
	],
]
df_distance = pd.DataFrame(distance_rows, columns=distance_columns)
print()
print(df_distance)

# Freq DataFrame V-N
freq_vn_columns = ["lemma", "celkem", "VNP (%)", "modus vzdálenosti VNP", "ø vzdálenost VNP", "ostatní (%)", "sort_by"]
freq_vn_rows = []
for item in data_vn:
	freq_vn_rows.append(
		[item.getLemma(), item.getTotal(), item.getCountsWithPercentage("vnp"), item.getWordcountsMode(),
		 item.getWordcountsMean(), item.getCountsWithPercentage("ostatni"), item.getPercentage("vnp")])
df_freq_vn = pd.DataFrame(freq_vn_rows, columns=freq_vn_columns)
df_freq_vn = df_freq_vn.sort_values("sort_by", ascending=False)
df_freq_vn = df_freq_vn.drop("sort_by", axis=1)

# Freq DataFrame N-V
freq_nv_columns = ["lemma", "celkem", "VNP + vztažné %", "VNP (%)", "modus vzdálenosti VNP", "ø vzdálenost VNP",
				   "vztažné (%)",
				   "ostatní (%)", "sort_by"]
freq_nv_rows = []
for item in data_nv:
	freq_nv_rows.append([item.getLemma(), item.getTotal(),
						 item.getCountsWithPercentageVnpVztazne(),
						 item.getCountsWithPercentage("vnp"), item.getWordcountsMode(), item.getWordcountsMean(),
						 item.getCountsWithPercentage("vztazne"), item.getCountsWithPercentage("ostatni"),
						 item.getPercentageVnpVztazne()])
df_freq_nv = pd.DataFrame(freq_nv_rows, columns=freq_nv_columns)
df_freq_nv = df_freq_nv.sort_values("sort_by", ascending=False)
df_freq_nv = df_freq_nv.drop("sort_by", axis=1)

# Collocations
colloc_columns = ["lemma", "celkem", "VNP + vztažné (%)", "ostatní (%)", "logDice", "logDice N pořadí", "sort_by"]
colloc_rows = []
merged = {}
for item in data:
	if item.lemma in merged:
		merged[item.lemma].add("vnp", item.getCounts("vnp"))
		merged[item.lemma].add("vztazne", item.getCounts("vztazne"))
		merged[item.lemma].add("ostatni", item.getCounts("ostatni"))
	else:
		item.type = "merged"
		item.total = 0
		merged[item.lemma] = item

for item in merged.values():
	colloc_rows.append([
		item.getLemma(), item.getTotal(), item.getCountsWithPercentageVnpVztazne(),
		item.getCountsWithPercentage("ostatni"), collocations.getLogDiceScore(item.lemma),
		collocations.getNOrder(item.lemma), item.getPercentageVnpVztazne()
	])
df_colloc = pd.DataFrame(colloc_rows, columns=colloc_columns)
df_colloc = df_colloc.sort_values("sort_by", ascending=False)
df_colloc = df_colloc.drop("sort_by", axis=1)

# Create a Pandas Excel writer using XlsxWriter as the engine.
# https://xlsxwriter.readthedocs.io/example_pandas_multiple.html
writer = pd.ExcelWriter(parent_directory + '/_data/freq.xlsx', engine='xlsxwriter')

# Write each dataframe to a different worksheet.
df_basic.to_excel(writer, sheet_name='Freq', index=False)
df_summary.to_excel(writer, sheet_name='Summary', index=False)
df_summary_cite.to_excel(writer, sheet_name='Cite', index=False)
df_distance.to_excel(writer, sheet_name='Cite Distance', index=False)
df_freq_vn.to_excel(writer, sheet_name='Cite Freq V-N', index=False)
df_freq_nv.to_excel(writer, sheet_name='Cite Freq N-V', index=False)
df_colloc.to_excel(writer, sheet_name='Cite Colloc', index=False)

# Close the Pandas Excel writer and output the Excel file.
writer.save()

print()
print('✅ Excel uložen')
