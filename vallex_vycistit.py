import argparse
import os
import re
import czech_sort

# - procházet jednotlivé řádky - lemma
# - uložit 0/1 jestli je to VNP nebo není do TMP složky a pak nahradit

# Parametry
parser = argparse.ArgumentParser()
parser.add_argument('directory', help='Název složky (slovesa), ve které se bude čistit vallex')
args = parser.parse_args()

directory = './' + args.directory


def clean_vallex_rows(row):
	row = row.replace(' blu-n-', ',')
	row = row.replace('blu-n-', '')
	row = re.sub('-\d', '', row)
	row = row.replace('-', ', ')
	row = row.replace(';', ',')
	row = row.replace('\n', '')
	row = row.replace(',', ', ')
	row = row.replace('  ', ' ')
	return row


def clean_and_unique(file_name):
	if os.path.isfile(directory + '/' + file_name + '.txt'):
		lvc = []
		# Otevřít soubor
		with open(directory + '/' + file_name + '.txt', "r", encoding='utf-8') as input_file, open(
				directory + '/' + file_name + '_unique.txt', "w", newline="", encoding='utf-8') as output_file:

			# Procházet jednotlivé řádky
			for row in input_file:
				row = clean_vallex_rows(row)
				lvc += row.split(', ')

			input_file.close()

			# Získat unikátní hodnoty a seřadit
			lvc = sorted(list(set(lvc)), key=czech_sort.key)

			for v in lvc:
				output_file.write(v + "\n")

			output_file.close()


# Vybrat složku
if os.path.isdir(directory):
	clean_and_unique('vallex')
	clean_and_unique('vallex_working')
