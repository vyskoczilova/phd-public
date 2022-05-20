import argparse
from scripts.helpers import get_vnp_dict

parser = argparse.ArgumentParser()
parser.add_argument(
	'directory', help='Název složky (slovesa), ze které se bude čerpat')
parser.add_argument("-a", "--anotovano",
					help="Hodnota sloupce \"VNP?\"", action="store", default="1")
args = parser.parse_args()

vnps = get_vnp_dict('./' + args.directory, args.anotovano)

print(", ".join(vnps))
