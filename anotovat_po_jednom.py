import argparse
import os
from scripts.helpers import Helpers
from scripts.concordance import ConcordanceRow
import pandas as pd

# https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas

# Parametry
parser = argparse.ArgumentParser()
parser.add_argument('directory', help='Název složky (slovesa), ve které se budou anotovat příklady')
parser.add_argument('noun', help='Název složky (podstatného jména), ve které se budou anotovat příklady')
parser.add_argument("-t", "--type",
					help="Typ konstrukce (\"N-V\" nebo \"V-N\")", action="store", default="N-V")

args = parser.parse_args()

# Zjisti jestli složka existuje
directory = './' + args.directory + '/' + args.noun
if not os.path.isdir(directory):
	print("Adresář neexistuje.")
	quit()

# Zjisti jméno souboru s konkordancí
output_file_name = args.type + '_anotovano.csv'
source_file = Helpers.csv_file_starts_with(directory, args.type + '_kontext-conc')
if not source_file:
	print("Soubor k anotaci neexistuje.")
	quit()

# Načti čistý zdroj nebo upravený zdroj
read_from = output_file_name if os.path.isfile(directory + '/' + output_file_name) else source_file
df = pd.read_csv(directory + '/' + read_from, sep=";", index_col=0, dtype=str, keep_default_na=False)
df = df.reset_index()
new_values = []

breaker = False  # our mighty loop exiter!

# Projdi příklad po příkladu
for index, row in df.iterrows():
	if ("VNP?" not in df.columns or row["VNP?"] == "") and not breaker:
		c_row = ConcordanceRow(row["left"], row["kwic"], row["right"])

		print()
		print("---------------------------")
		print()
		print('[' + str(index + 1) + '/' + str(df.shape[0]) + ']')
		print(c_row.get_sententce(True))

		while True:
			is_vnp = input('\nJe to příklad VNP?\n0 = ne, 1 = ano, 2 = možná, 3 = vztažné, x = skončit: ')
			if is_vnp == 'x':
				breaker = True
				new_values.append("")
				break
			if is_vnp not in ['0', '1', '2', '3']:
				print("> Neplatná hodnota.")
				continue
			else:
				new_values.append(is_vnp)
				break

	# uložit hodnotu
	elif "VNP?" in df.columns:
		new_values.append(row["VNP?"])
	else:
		new_values.append("")

# Ulož anotaci
df["VNP?"] = new_values

# Odeber všechny prázdné sloupce
# https://www.geeksforgeeks.org/drop-empty-columns-in-pandas/
df.replace("", float("NaN"), inplace=True)
df.dropna(how='all', axis=1, inplace=True)

# Ulož csv
df.to_csv(directory + '/' + output_file_name, sep=";", encoding="utf-8", index=False)

print()
print('✅ uloženo')
