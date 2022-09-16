import argparse
import os
import pandas as pd
from scripts.concordance import ConcordanceRow
from scripts.helpers import Helpers, get_pos_from_detailed, prcnt_wrap, prcnt, merge_prep_lemmas
from colorama import Fore, init
from scripts.rich_excel_writer import RichExcelWriter

init()

def count_lemmas(data, in_pos, filter_pos_value):
	counts = {}
	for pos_pretty, data_values in data.items():
		if pos_pretty in in_pos:
			pos = pos_pretty.split("-")
			prep_index = pos.index(filter_pos_value)
			for lemmas in data_values:
				lemma = merge_prep_lemmas(lemmas[prep_index])
				if lemma not in counts:
					counts[lemma] = 0
				counts[lemma] += 1
	return counts


# Parameters
parser = argparse.ArgumentParser()
parser.add_argument('directory', help='Název složky (slovesa), ve které se budou doplňovat informace')
args = parser.parse_args()

# Check if directory exists
parent_directory = './' + args.directory + '/'
if not os.path.isdir(parent_directory):
	print("Adresář neexistuje.")
	quit()

# Load lost of files
files = []
for f in os.listdir(parent_directory):
	if f.endswith("_anotovano.csv"):
		files.append(parent_directory + f)

merged_columns = ["sloveso", "left", "kwic", "right", "pos", "anotovano"]
merged_rows = []

data_working_pos = {}
max_consecutive_empty_rows_till_break = 50  # So we don't need to loop throught the whole file

# Go through individual files and extract data
for file in files:
	df = pd.read_csv(file, sep=";", index_col=0, dtype=str, keep_default_na=False)
	df = df.reset_index()
	consecutive_empty_rows = 0

	verb_group = file[len(parent_directory):-len("_anotovano.csv")].replace("_", "/")

	for index, row in df.iterrows():

		if consecutive_empty_rows > max_consecutive_empty_rows_till_break:
			break
		elif row["VNP?"] != "" and row["VNP?"] != "x":
			c_row = ConcordanceRow(row["left"], row["kwic"], row["right"])

			pos_formatted = c_row.kwic_get_pos_formatted()
			merged_rows.append([verb_group, c_row.strip_lemma_and_tag('left'), c_row.strip_lemma_and_tag('kwic'),
								c_row.strip_lemma_and_tag('right'), pos_formatted, row["VNP?"]])

			if pos_formatted not in data_working_pos.keys():
				data_working_pos[pos_formatted] = [0, 0, 0, 0]

			try:
				data_working_pos[pos_formatted][int(row["VNP?"])] += 1
			except:
				print()
				print("CHYBA:")
				print("soubor: " + Fore.YELLOW + file + Fore.RESET)
				print("řádek: " + Fore.YELLOW + str(index + 2) + Fore.RESET)
				print("neočekávaný znak: " + Fore.YELLOW + row["VNP?"] + Fore.RESET)
				print()
				quit()
		else:
			consecutive_empty_rows += 1

# Create a Pandas Excel writer using XlsxWriter as the engine.
# https://xlsxwriter.readthedocs.io/example_pandas_multiple.html
writer = RichExcelWriter(parent_directory + '/_data/acc_all.xlsx')

# colors https://devdreamz.com/question/129769-write-pandas-dataframe-to-excel-with-xlsxwriter-and-include-write-rich-string
workbook = writer.book
bold = workbook.add_format({'bold': True})
italic = workbook.add_format({'italic': True})

examples = {
	"V-N" : ["Stejně ale ", bold, "chovám naději", ", že skutečnost je jiná."],
	"V-A-N" : ["Přesto musím ", bold, "přebírat plnou odpovědnost", " za všechny své činy [...]."],
	"V-P-N" : ["Ještě žes ", bold, "našel tu odvahu", " a řekl mi pravdu."],
	"V-P-A-N": ["Již příliš dlouho ", bold, "uplatňují své přemrštěné nároky", " na ovlivňování našich životů."],
	"V-D-A-N": ["Na levém kraji obrany ", bold, "podal velmi dobrý výkon", "."],
	"V-A-A-N": ["[V]dova ", bold, "pojala šílený vdovský úmysl", " učinit pánem nad rozháraným koncertním jednatelstvím mě."],
	"V-D-N": ["ČNB ovšem následně ", bold, "vydala opět rozhodnutí", " o pokutě 1,7 milionu korun [...]."],
	"V-R-N-N": ["Dnes by měl soud ", bold, "vynést nad Tichým rozsudek", "."],
	"V-R-N-A-N": [bold, "Má na Broadwayi domovské právo", "."],
	"V-R-P-A-N": ["Od začátku ji ochraňoval, ", bold, "jevil o ni upřímný zájem", " a od okamžiku, kdy se na něho poprvé okouzleně podívala, stal se pro ni hrdinou [...]."],
	"N-R-P-V": ["Když Karin opět promluví, slyším, že už ", bold, "boj proti tomu vzdala", "."],
	"N-R-A-N-V": ["V úterý totiž ", bold, "pokus o stejný vrchol vzdal", " jiný vyhlášený osmitisícovkář, Španěl Carlos Pauner."],
	"V-A-J-A-N": [bold, "Podat poctivý a kvalitní výkon ", "podpořený dobrou koncovkou."],
	"V-R-A-N-N": ["Doufám, že si z toho hráči ", bold, "vezmou do dalších utkání ponaučení", "." ],
	"V-N-J-N": ["Jen ", bold, "našli sílu a odvahu", " se ke svému problému přiznat."],
	"V-R-A-N-A-N": [bold, "Získal na hlavní pole minutový náskok", ", ale to bylo všechno."],
	"V-T-A-N": ["Padang o svou novou partnerku ", bold, "projevuje opravdu velký zájem", "."],
	"V-R-P-N-N": ["[P]ůvodní nájemce ", bold, "má na jeho vystěhování čas", " do konce března."],
	"V-R-N-N-N": [bold, "Vznáším proti generálu Stoneovi stížnost", "."],
	"V-A-N-J-N": ["Někdy je nutné ", bold, "přijmout tvrdá rozhodnutí a opatření", ", která nemusí každý vítat s radostí."],
	"V-R-P-P-N": ["Když si vytíral chlebovou kůrkou omáčku, ", bold, "vydával ze sebe nějaké zvuky", " naznačující spokojenost."],
	"V-R-P-N": ["Riskoval tím však, že se ho později bude Junk vyptávat na jeho telepatické kouzlo a ", bold, "pojme vůči němu podezření", "."],
	"N-R-N-V": ["Ostrava čeká, jaký ", bold, "postoj k věci zaujme", " vedení klubu z Uherského Hradiště."],
	"V-R-P-N-A-N": ["Oni ", bold, "uplatňovali podle svého chápání přirozené právo", " majorit vůči minoritám."],
	"V-R-N-P-N": ["Od začátku nám kladl na srdce, že nemáme ", bold, "vyvíjet na Blunta žádný nátlak", ", aby neemigroval."],
}


df_merged = pd.DataFrame(merged_rows, columns=merged_columns)

# Only POS
only_pos_rows = []
only_pos_columns = ["POS", "příklad", "počet APKS\n(podíl ze všech APKS v %)","jiné", "sort_by"]
total_vnp = sum(v[1] for k, v in data_working_pos.items())
for key_pos, value in data_working_pos.items():
	pos = key_pos.split("-")
	n_vnp = value[1]
	example = examples[key_pos] if key_pos in examples else ""
	only_pos_rows.append(
		[key_pos, example, prcnt_wrap(before=str(n_vnp) + " (", count=n_vnp, total=total_vnp), value[0],
		 n_vnp])
df_only_pos = pd.DataFrame(only_pos_rows, columns=only_pos_columns)
df_only_pos = df_only_pos.sort_values("sort_by", ascending=False)

only_pos_prcnt = 0;
only_pos_cumulative_coll = []
for index, row in df_only_pos.iterrows():
	only_pos_prcnt += prcnt(row["sort_by"], total_vnp)
	only_pos_cumulative_coll.append(str(round(only_pos_prcnt, 2)).replace(".", ","))

df_only_pos = df_only_pos.drop("sort_by", axis=1)
df_only_pos.insert(loc=3, column='kumulativní %',
								   value=only_pos_cumulative_coll)

# Write each dataframe to a different worksheet.
df_merged.to_excel(writer, sheet_name='data', index=False)
df_only_pos.to_excel(writer, sheet_name='POS', index=False)

# Close the Pandas Excel writer and output the Excel file.
writer.save()
print('✅ Excel uložen')
