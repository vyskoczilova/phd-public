import argparse
import os
import re
import csv
import shutil
from scripts.concordance import Concordance
from scripts.word_lists import WordLists

# Parameters
parser = argparse.ArgumentParser()
parser.add_argument(
	'directory', help='Název složky (slovesa), ve které se budou anotovat příklady')
args = parser.parse_args()
directory = './' + args.directory


#######################
#   Enter your data   #
#######################

# Wordlist in TXT (one word per line); directory is the opened directory
data_wordlists = {
	"VALLEX": directory + "/vallex_unique.txt",
	"Radimský": directory + "/radimsky.txt",
	"VALLEX - working": directory + "/vallex_working_unique.txt"
}

# Number of examples to show
data_number_of_examples = 20

#################################
#   Script itself starts here   #
#################################


verbs = args.directory.replace('_', '/')
rename = False

# Load previously accepted LVCS
accepted_vnps = WordLists()
for wordlist_title, wordlist_file in data_wordlists.items():
	accepted_vnps.loadWordList(wordlist_file, wordlist_title)


# Load the concordance
data = Concordance(args.directory)
data.parse_concordance()

if os.path.isdir(directory):

	# Have we started annotating? Create a copy of the freq. file and work with it.
	if not os.path.isfile(directory + "/anotovano.csv"):

		# Work with the correct file with frequencies - contains "freq"
		for fname in os.listdir(directory):
			pattern = re.compile("^kontext-freq.*\\.csv$")
			if pattern.match(fname):
				shutil.copyfile(directory + '/' + fname, directory + '/anotovano.csv')

	# Open the file
	with open(directory + '/anotovano.csv', "r", encoding='utf-8') as input_file, open(
			directory + '/_tmp_anotovano.csv', "w", newline="", encoding='utf-8') as output_file:

		csv_reader = csv.reader(input_file, delimiter=';')
		csv_writer = csv.writer(output_file, delimiter=";")

		breaker = False  # our mighty loop exiter!

		# Go through the rows
		for row in csv_reader:

			# Not annotated or no header?
			if (len(row) == 4 or row[5] == "") and not breaker and row[1] != "lemma":

				noun = row[1]

				if len(row) != 4:
					del row[4:]  # truncate if there are "empty" cells (Modern CSV fix)

				# If already annotated as LVC, mark it.
				is_accepted_vnp = accepted_vnps.search(noun)
				if is_accepted_vnp:
					row.append("1")  # LVC?
					row.append(is_accepted_vnp)  # Who said so.

				# Annotate
				else:
					print()
					print("---------------------------")
					print()

					# Print examples
					data.print_examples_from_kwic(noun, data_number_of_examples)

					# Anotate
					while True:

						is_vnp = input(
							'\n🟨 Je "' + verbs + ' ' + noun + '" VNP?\n0 = ne, 1 = ano, 2 = možná, x = skončit: ')
						if is_vnp == 'x':
							breaker = True
							break
						if is_vnp not in ['0', '1', '2']:
							print("> Neplatná hodnota.")
							continue
						else:

							row.append(is_vnp)
							row.append("KV")

							if is_vnp == '1' or is_vnp == '2':
								get_example = input('\n🟨 Vložte příklad nebo nechte prázdné:').strip()
								row.append(get_example)

								get_note = input(
									'\n🟨 Vložte poznámku nebo nechte prázdné:').strip()
								row.append(get_note)
							else:
								row.append("")
								row.append("")

							break

				# Save
				csv_writer.writerow(row)

			# Fix headers
			elif row[1] == "lemma" and len(row) == 4:
				row.append("VNP?")
				row.append("kdo")
				row.append("příklad")
				row.append("poznámka")
				csv_writer.writerow(row)
			else:
				csv_writer.writerow(row)

		input_file.close()
		output_file.close()

# Remove the old file and tmp
os.remove(directory + '/anotovano.csv')
os.rename(directory + '/_tmp_anotovano.csv', directory + '/anotovano.csv')
print()
print('✅ uloženo')
