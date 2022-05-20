import argparse
import os
import re
import csv
import shutil
from scripts.concordance import Concordance
from scripts.word_lists import WordLists
from scripts.csv_file import CsvFile

# Parametry
parser = argparse.ArgumentParser()
parser.add_argument('directory', help='Název složky (slovesa), ve které se budou anotovat příklady')
args = parser.parse_args()

directory = './' + args.directory
verbs = args.directory.replace('_', '/')
rename = False

# Načíst už schválené VNP
accepted_vnps = WordLists()
accepted_vnps.loadWordList(directory + "/vallex_unique.txt", "VALLEX")
accepted_vnps.loadWordList(directory + "/radimsky.txt", "Radimský")
accepted_vnps.loadWordList(directory + "/vallex_working_unique.txt", "VALLEX - working")

# Načíst staré soubory, pokud existuji
old_annotation = CsvFile(directory + "/old/anotovano.csv")
old_annotation.load_with_headers()

# Načíst konkordanci
data = Concordance(args.directory)
data.parse_concordance()

# Vybrat složku
if os.path.isdir(directory):

	# Ještě jsme nezahájili anotaci? Vytvoř kopii freq. souboru a tu dál upravuj.
	if not os.path.isfile(directory + "/anotovano.csv"):
		# Pracovat se správným souborem s frekvencemi - obsahuje "freq"
		for fname in os.listdir(directory):
			pattern = re.compile("^kontext-freq.*\\.csv$")
			if pattern.match(fname):
				shutil.copyfile(directory + '/' + fname, directory + '/anotovano.csv')

	# Otevřít soubor
	with open(directory + '/anotovano.csv', "r", encoding='utf-8') as input_file, open(
			directory + '/_tmp_anotovano.csv', "w", newline="", encoding='utf-8') as output_file:

		csv_reader = csv.reader(input_file, delimiter=';')
		csv_writer = csv.writer(output_file, delimiter=";")

		breaker = False  # our mighty loop exiter!

		# Procházet jednotlivé řádky
		for row in csv_reader:

			# Neanotováno nebo to není hlavička?
			if (len(row) == 4 or row[5] == "") and not breaker and row[1] != "lemma":

				noun = row[1]
				old_verb_annotation = old_annotation.select_where_column_value("lemma", noun,
																			   ["VNP?", "kdo", "příklad", "poznámka"])

				if len(row) != 4:
					del row[4:]  # truncate if there are "empty" cells (Modern CSV fix)

				# Pokud už někdo říká, že je to VNP označ to.
				is_accepted_vnp = accepted_vnps.search(noun)
				if is_accepted_vnp:
					row.append("1")  # VNP?
					row.append(is_accepted_vnp)  # kdo
					# zkus štěstí, kdyby byla nějaký stará anotace
					if old_verb_annotation:
						row.append(old_verb_annotation["příklad"])
						row.append(old_verb_annotation["poznámka"])

				# Zkontroluj starou anotaci, je-li nějaká
				elif old_verb_annotation and old_verb_annotation["VNP?"] != "":
					row.append(old_verb_annotation["VNP?"])
					row.append(old_verb_annotation["kdo"])
					row.append(old_verb_annotation["příklad"])
					row.append(old_verb_annotation["poznámka"])

				# Jinak zjisti, co si myslím
				else:
					print()
					print("---------------------------")
					print()

					# Vytisknout příklady
					data.print_examples_from_kwic(noun, 20)

					# Oanotovat
					while True:

						# Je to VNP nebo není?
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

				# Zapsat hodnoty
				csv_writer.writerow(row)
			# zaktualizuj hlavičky, pokud je třeba
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

# Odstranit starý soubor a přejmenovat zpět
os.remove(directory + '/anotovano.csv')
os.rename(directory + '/_tmp_anotovano.csv', directory + '/anotovano.csv')
print()
print('✅ uloženo')
