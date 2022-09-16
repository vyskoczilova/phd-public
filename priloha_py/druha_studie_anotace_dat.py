import argparse
import os
from scripts.helpers import Helpers
from scripts.concordance import ConcordanceRow
import pandas as pd


# Parameters
parser = argparse.ArgumentParser()
parser.add_argument('directory', help='Název složky (slovesa), ve které se budou anotovat příklady')
parser.add_argument('noun', help='Název předpony souboru (podstatného jména), ze které se budou anotovat příklady')
parser.add_argument('-oc', '--output_column', help='Název sloupce, do kterého se budou anotovat příklady', action='store', default='VNP?')

args = parser.parse_args()

# Check if directory exists
directory = './' + args.directory + "/"
if not os.path.isdir(directory):
	print("Adresář neexistuje.")
	quit()

# Get concordance file name
output_file_name = args.noun + '_anotovano.csv'
source_file = Helpers.csv_file_starts_with(directory, args.noun + '_kontext-conc')
if not source_file and args.output_column == 'VNP?':
	print("Soubor k anotaci neexistuje.")
	quit()
elif not os.path.isfile(directory + output_file_name):
	print("Soubor s anotacemi neexistuje existuje.")
	quit()

# Load source
read_from = output_file_name if os.path.isfile(directory + output_file_name) else source_file
df = pd.read_csv(directory + '/' + read_from, sep=";", index_col=0, dtype=str, keep_default_na=False)
df = df.reset_index()
new_values = []

breaker = False  # our mighty loop exiter!

allowed_pos = [
	"V-N",
	"V-A-N",
	"V-P-N",
	"V-R-P-A-N",
	"V-D-A-N",
	"V-R-P-N",
	"V-R-N-A-N",
	"V-R-N-N",
	"N-R-P-V",
	"V-P-A-N",
	"V-N-J-N",
	"V-A-N-J-N",
	"V-R-P-N-A-N",
	"N-R-N-V",
	"V-R-A-N-A-N",
	"V-D-N",
	"V-T-A-N",
	"V-A-A-N",
	"V-R-N-P-N",
	"V-R-P-N-N",
	"V-R-N-N-N",
	"V-A-J-A-N",
	"V-R-P-P-N",
	"V-R-A-N-N",
	"N-R-A-N-V",
]
allowed_detailed_pos = ["J^", "P5", "P6", "P7", "P8", "PD", "PL", "PP", "PS", "PW", "PZ"]
only_dat_prep = ["V-R-P-N", "N-R-N-V"]
dat_prep = ["k", "ke", "proti", "vůči", "díky"]
countAllowedStructures = 0
maxAllowedStructures = 100

# Loop through rows
for index, row in df.iterrows():

	if (args.output_column not in df.columns or row[args.output_column] == "" or row[args.output_column] == "x") and not breaker:

		c_row = ConcordanceRow(row["left"], row["kwic"], row["right"])
		pos_formatted = c_row.kwic_get_pos_formatted()

		# Only allowed structures
		if pos_formatted in allowed_pos:

			if countAllowedStructures < maxAllowedStructures:
				#
				pos = c_row.kwic_get_pos()
				pos_detailed = c_row.kwic_get_pos_detailed()

				# skip if not allowed value in second position (pronouns)
				if "P" in pos_formatted and pos_detailed[pos.index("P")] not in allowed_detailed_pos:
					new_values.append("x")
					continue

				# skip if not allowed value in second position (conjugations)
				if "J" in pos_formatted and pos_detailed[pos.index("J")] not in allowed_detailed_pos:
					new_values.append("x")
					continue

				# skip if not allowed lemma for selected structures:
				if pos_formatted in only_dat_prep:
					lemmas = c_row.kwic_get_lemmas()
					if lemmas[pos.index("R")] not in dat_prep:
						new_values.append("x")
						continue

				print()
				print("---------------------------")
				print()
				print('[' + str(countAllowedStructures + 1) + '/' + str(maxAllowedStructures) + ']')
				print(c_row.get_sententce(True))

				while True:
					is_vnp = input('\nJe to příklad APKS?\n0 = ne, 1 = ano, 2 = možná, 3 = vztažné, x = skončit: ')
					if is_vnp == 'x':
						breaker = True
						new_values.append("")
						break
					if is_vnp not in ['0', '1', '2', '3']:
						print("> Neplatná hodnota.")
						continue
					else:
						countAllowedStructures += 1
						new_values.append(is_vnp)
						break

			else:
				new_values.append("")
		else:
			new_values.append("x")
	#
	elif args.output_column in df.columns:
		new_values.append(row[args.output_column])
		if row[args.output_column] != "x":
			countAllowedStructures += 1
	else:
		new_values.append("")

# Add a new columns
df[args.output_column] = new_values

# Remove empty freq_vn_columns
# https://www.geeksforgeeks.org/drop-empty-columns-in-pandas/
df.replace("", float("NaN"), inplace=True)
df.dropna(how='all', axis=1, inplace=True)

# Remove not useful structures
df = df[df[args.output_column] != "x"]
# Works only with 10 000 rows - corresponds to the maximum limit and solves the problem with the size of files
df = df.head(10000)

# Save CSV
df.to_csv(directory + '/' + output_file_name, sep=";", encoding="utf-8", index=False)

print()
print('✅ uloženo')
