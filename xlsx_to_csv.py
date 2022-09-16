import pandas as pd
import argparse
import os
import sys
from unidecode import unidecode

parser = argparse.ArgumentParser()
parser.add_argument(
    'file', help='Excel, který se má převést na CSV')
parser.add_argument("-t", "--tabs",
                    help="Záložky, které se mají vyexportovat (odděleno čárkou). Bez specifikace se exportují všechny.", action="store", default='')
args = parser.parse_args()

tabs = args.tabs.split(",") if args.tabs else None
filename_without_extension = args.file.split(".")[0]

if not os.path.isfile(args.file):
    sys.exit("Soubor neexistuje")


def clean_filename(filename):
    return unidecode(filename.lower().replace(" ", "_"). replace("+", "").replace("__", "_"))


for sheet_name, df in pd.read_excel(args.file, index_col=0, sheet_name=None).items():
    if tabs and sheet_name not in tabs:
        continue
    filename = filename_without_extension + "_" + sheet_name + \
        ".csv"
    if tabs and len(tabs) == 1:
        filename = filename_without_extension + ".csv"
    df.to_csv(clean_filename(filename), index=False, encoding='utf-8')
