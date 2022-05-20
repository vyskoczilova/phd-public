import argparse
import os
from scripts.concordance import Concordance

# Parametry
parser = argparse.ArgumentParser()
parser.add_argument('directory', help='Název složky (slovesa), ve které se bude hledat')
parser.add_argument('lemma', help='KWIC lemma')
parser.add_argument("-l", "--lines",
					help="Maximální počet řádku", action="store", default=50)
args = parser.parse_args()

if os.path.isdir(args.directory):
	data = Concordance(args.directory)
	data.parse_concordance()
	data.print_examples_from_kwic(args.lemma, args.lines)

else:
	print("CHYBA: Zadaný adresář neexistuje.")
