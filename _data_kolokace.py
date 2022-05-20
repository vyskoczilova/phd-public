import argparse
import os
from scripts.helpers import Annotate, Helpers, get_vnp_dict
import pandas as pd

from scripts.word_lists import WordLists

parser = argparse.ArgumentParser()
parser.add_argument('directory', help='Název složky (slovesa), ve které se budou anotovat příklady')
args = parser.parse_args()

# Zjisti jestli složka existuje
directory = './' + args.directory
if not os.path.isdir(directory):
	print("Adresář neexistuje.")
	quit()

# Zjisti jméno souboru s kolokacemi
source_file = Helpers.csv_file_starts_with(directory, "kontext-coll_")
if not source_file:
	print("Soubor k anotaci neexistuje.")
	quit()

df = pd.read_csv(directory + '/' + source_file, sep=";", index_col=0, dtype=str, keep_default_na=False)
df = df.reset_index()

if "lemma" not in df.columns:
	print("Doplň hlavičku k souboru s kolokacemi.")
	quit()

pos = []
is_vnp = []
annotate = Annotate()

# Seznamy VNP
# Načíst už schválené VNP
accepted_vnps = WordLists()
accepted_vnps.loadWordList(directory + "/vallex_unique.txt", "VALLEX")
accepted_vnps.loadWordList(directory + "/radimsky.txt", "Radimský")
accepted_vnps.loadWordList(directory + "/vallex_working_unique.txt", "VALLEX - working")
vnps = get_vnp_dict(directory)

# Projdi příklad po příkladu
for index, row in df.iterrows():
	pos.append(annotate.get_pos(row["lemma"]))
	# Pokud už někdo říká, že je to VNP označ to.
	is_accepted_vnp = accepted_vnps.search(row["lemma"])
	if is_accepted_vnp:
		is_vnp.append(is_accepted_vnp)
	elif row["lemma"] in vnps:
		is_vnp.append("KV")
	else:
		is_vnp.append("")

# Přidej nový sloupec
df["POS"] = pos
df["VNP?"] = is_vnp

# Ulož csv
print()
df.to_csv(directory + '/_data/collocations.csv', sep=";", encoding="utf-8", index=False)
print('✅ CSV uloženo')

df.to_excel(directory + '/_data/collocations.xlsx', sheet_name="Freq")
print('✅ Excel uložen')
