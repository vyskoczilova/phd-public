import argparse
import os
from scripts.helpers import Annotate, Helpers, get_vnp_dict
import pandas as pd

from scripts.word_lists import WordLists

parser = argparse.ArgumentParser()
parser.add_argument('directory', help='Název složky (slovesa), kde jsou anotované případy')
args = parser.parse_args()

# Check if directory exists
directory = './' + args.directory
if not os.path.isdir(directory):
	print("Adresář neexistuje.")
	quit()

#######################
#   Enter your data   #
#######################

# Wordlist in TXT (one word per line); directory is the opened directory
data_wordlists = {
	"VALLEX": directory + "/vallex_unique.txt",
	"Radimský": directory + "/radimsky.txt",
	"VALLEX - working": directory + "/vallex_working_unique.txt"
}

# Old annotations to merge in if any (e.g.)
data_old_annotations = directory + "/old/anotovano.csv"

# Number of examples to show
data_number_of_examples = 20

#################################
#   Script itself starts here   #
#################################

# Get file with collocations
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
annotate = Annotate(directory)

# LVCS
accepted_vnps = WordLists()
for wordlist_title, wordlist_file in data_wordlists.items():
	accepted_vnps.loadWordList(wordlist_file, wordlist_title)

vnps = get_vnp_dict(directory)

# Go through rows
for index, row in df.iterrows():
	pos.append(annotate.get_pos(row["lemma"]))
	# If someone already said it's a LVC, mark it.
	is_accepted_vnp = accepted_vnps.search(row["lemma"])
	if is_accepted_vnp:
		is_vnp.append(is_accepted_vnp)
	elif row["lemma"] in vnps:
		is_vnp.append("KV")
	else:
		is_vnp.append("")

# Add new columns
df["POS"] = pos
df["APKS?"] = is_vnp

print()

# Save

df.to_csv(directory + '/_data/collocations.csv', sep=";", encoding="utf-8", index=False)
print('✅ CSV uloženo')

df.to_excel(directory + '/_data/collocations.xlsx', sheet_name="Freq")
print('✅ Excel uložen')
