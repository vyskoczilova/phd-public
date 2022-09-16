import argparse
import os
import pandas as pd
from scripts.concordance import ConcordanceRow
from scripts.helpers import Helpers, get_pos_from_detailed, prcnt_wrap, prcnt, merge_prep_lemmas
from colorama import Fore, init
from scripts.rich_excel_writer import RichExcelWriter

init()


# Count lemmas
def count_lemmas(data, in_pos, filter_pos_value):
	counts = {}
	for pos_pretty, data_values in data.items():
		if pos_pretty in in_pos:
			pos = pos_pretty.split("-")
			prep_index = pos.index(filter_pos_value)
			for lemmas in data_values:
				lemma = merge_prep_lemmas(lemmas[prep_index])
				if lemma not in counts:
					counts[lemma] = 0
				counts[lemma] += 1
	return counts


# Parameters
parser = argparse.ArgumentParser()
parser.add_argument('directory', help='Název složky (slovesa), ve které se budou doplňovat informace')
args = parser.parse_args()

# Check if directory exists
parent_directory = './' + args.directory + '/'
if not os.path.isdir(parent_directory):
	print("Adresář neexistuje.")
	quit()

# Získej seznam souborů
files = Helpers.get_list_of_annotated_files(parent_directory)

# 0 = "není"
# 1 = "je"
# 2 = "nevíme"
# 3 = "vztažné"
data_working_pos = {}
data_working_pos_detailed = {}
data_working_pos_detailed_simplified = {}
data_working_pos_prep_is_vnp = {}
data_working_pos_prep_not_vnp = {}
data_working_negace = {"kladna": 0, "zaporna": 0}  # kladné a záporné věty - NOT USED
data_working_txtype = {}

# Projdi jednotlivé soubory a vytáhni si data
for file in files:
	df = pd.read_csv(file, sep=";", index_col=0, dtype=str, keep_default_na=False)
	df = df.reset_index()

	for index, row in df.iterrows():
		c_row = ConcordanceRow(row["left"], row["kwic"], row["right"])
		pos_formatted = c_row.kwic_get_pos_formatted()
		pos_detailed_formatted = c_row.kwic_get_pos_detailed_formatted()
		pos_detailed_simplified_formatted = pos_detailed_formatted[0:1] + pos_detailed_formatted[
																		  2:-1]  # Drop first and last char

		if pos_formatted not in data_working_pos.keys():
			data_working_pos[pos_formatted] = [0, 0, 0, 0]

		if pos_detailed_formatted not in data_working_pos_detailed.keys():
			data_working_pos_detailed[pos_detailed_formatted] = [0, 0, 0, 0]

		if pos_detailed_simplified_formatted not in data_working_pos_detailed_simplified.keys():
			data_working_pos_detailed_simplified[pos_detailed_simplified_formatted] = [0, 0, 0, 0]

		if row["VNP?"] == "1":
			if row["doc.txtype_group"] not in data_working_txtype:
				data_working_txtype[row["doc.txtype_group"]] = 0
			data_working_txtype[row["doc.txtype_group"]] += 1
			if c_row.verb_negation():
				data_working_negace["zaporna"] += 1
			else:
				data_working_negace["kladna"] += 1

		# získej lemma u předložek
		if "R" in pos_formatted:
			if row["VNP?"] == "1":
				if pos_formatted not in data_working_pos_prep_is_vnp:
					data_working_pos_prep_is_vnp[pos_formatted] = []
				data_working_pos_prep_is_vnp[pos_formatted].append(c_row.kwic_get_lemmas())

			elif row["VNP?"] == "0":
				if pos_formatted not in data_working_pos_prep_not_vnp:
					data_working_pos_prep_not_vnp[pos_formatted] = []
				data_working_pos_prep_not_vnp[pos_formatted].append(c_row.kwic_get_lemmas())

		try:
			data_working_pos[pos_formatted][int(row["VNP?"])] += 1
			data_working_pos_detailed[pos_detailed_formatted][int(row["VNP?"])] += 1
			data_working_pos_detailed_simplified[pos_detailed_simplified_formatted][int(row["VNP?"])] += 1
		except:
			print()
			print("CHYBA:")
			print("soubor: " + Fore.YELLOW + file + Fore.RESET)
			print("řádek: " + Fore.YELLOW + str(index + 2) + Fore.RESET)
			print("neočekávaný znak: " + Fore.YELLOW + row["VNP?"] + Fore.RESET)
			print()
			quit()

# print(data_working_negace)
# print(data_working_txtype) # {'FIC: beletrie': 1275, 'NMG: publicistika': 6036, 'NFC: oborová literatura': 794, 'TODO': 204, 'TODO empty': 2}
# 8106 bez todo

# Create a Pandas Excel writer using XlsxWriter as the engine.
# https://xlsxwriter.readthedocs.io/example_pandas_multiple.html
writer = RichExcelWriter(parent_directory + '/_data/pos.xlsx')

# colors https://devdreamz.com/question/129769-write-pandas-dataframe-to-excel-with-xlsxwriter-and-include-write-rich-string
workbook = writer.book
bold = workbook.add_format({'bold': True})
italic = workbook.add_format({'italic': True})

examples = {
	"V-N": ["Víš, jaké k tobě ", bold, "chová city", "."],
	"V-A-N": ["I já jsem ", bold, "choval literární ambice", "."],
	"N-V": ["Majitelka salonu vůči své svěřence žádné ", bold, "antipatie nechovala", "."],
	"V-P-N": ["On dnes vůči lidem i věcem ", bold, "nechová žádné iluze", "."],
	"V-R-P-A-N": [bold, "Chovali k sobě srdečnou nenávist", "."],
	"V-D-A-N": [bold, "Chovám také velký obdiv", " k filmům Miloše Formana."],
	"V-R-P-N": [bold, "Nechovám k tobě nepřátelství", "."],
	"V-R-N-A-N": [bold, "Chovám k mužům hluboký obdiv", "."],
	"V-R-N-N": ["Mladík ", bold, "chová ke komunistům odpor", "."],
	"N-R-P-V": ["Přízeň k němu ", bold, "chovala i císařovna Marie Terezie", "."],
	"V-P-A-N": ["Dnes ", bold, "chovají ta nejtemnější podezření", " celé tři pětiny Evropanů."],
	"V-N-J-N": ["Vždycky jsem se k nim snažil ", bold, "chovat respekt a úctu", "."],
	"V-A-N-J-N": [bold, "Chovám nesmírný obdiv a úctu ke Karlově univerzitě", "."],
	"V-R-P-N-A-N": [bold, "Chová ke svému otci smíšené pocity", "."],
	"N-R-N-V": ["Obránce Sýkora ", bold, "zášť k zámoří nechová", "."],
	"V-R-A-N-A-N": ["Také hráči ", bold, "chovají k dvaapadesátiletému stratégovi velký respekt", "."],
	"V-D-N": ["K Československu jsem ", bold, "chovala odedávna sympatie", "."],
	"V-T-A-N": ["Fanoušci k němu ", bold, "chovají až božskou úctu", "."],
	"V-A-A-N": ["Ta v srdci dodnes ", bold, "chová pevné levicové přesvědčení", "."],
	"V-R-N-P-N": [bold, "Nechovám vůči policii žádnou zášť", "."],
	"V-R-P-N-N": [bold, "Chovej k té vlajce respekt", "."],
	"V-R-N-N-N": ["Ten přiznává, že ", bold, "chová pro historii vinohradnictví slabost", "."],
	"V-A-J-A-N": ["K ní ", bold, "chovám obdivný a uctivý vztah", "."],
	"V-R-P-P-N": [bold, "Chovám k němu veškerou úctu", "."],
	"V-R-A-N-N": ["Ministerstvo školství", bold, " chová ke krajské samosprávě nedůvěru", "."],
	"N-R-A-N-V": [bold, "Lásku k silným mašinám chovají", " oba slavní bráchové."],
	"V-T-N": [bold, "Chovají totiž opovržení ", "vůči sociálním médiím a internetu jako takovému."],
	"P5": ["A co víc, ", bold, "chovám k nim respekt", ". (VB-RR-P5-NN)"],
	"PW": ["Ale ona ke mně ", bold, "nechovala žádné city", ". (Vp-PW-NN)"],
	"PD": ["Litujeme toho, protože ", bold, "chováme k tomuto lidu přátelský vztah", ". (VB-RR-PD-NN-AA-NN)"],
	"PZ": ["Věty sugerují představu, že ", bold, "chovám jakési sympatie",
		   " vůči KSČM, a tím hraničí se lží. (VB-PZ-NN)"],
	"P6": ["Lidé se zdraví a ", bold, "chovají k sobě úctu", ". (VB-RR-P6-NN)"],
	"PP": [bold, "Nechovám k tobě nepřátelství", ". (VB-RR-PP-NN)"],
	"P8": ["Lidé v Tatobitech ", bold, "chovají ke své lípě velikou úctu", ". (VB-RV-P8-NN-AA-NN)"],
	"PS": ["Jestli můj synovec ", bold, "chová vaše názory",
		   " v úctě, vezme je v potaz, i když se s vámi možná bude donekonečna hádat. (VB-PS-NN)"],
	"PL": ["Můžete ", bold, "chovat k veškerému sportu vyslovený odpor",
		   ", ale pro vašeho psa je každý pohyb odměnou. (Vf-RR-PL-NN-AA-NN)"],
	"P7": [bold, "Chovám si naději", ", že by byli také zvoleni. (VB-P7-NN)"],
	"N-Z-V": ["Mění", bold, " názory, chová", " se jinak na veřejnosti a jinak doma."],
	"N-Z-N-P-R-P-N-V-V": ["Absurdní příběh o tom, jak babička naplní svůj ", bold,
						  "sen, matka se ke svým dcerám přestane chovat ", "jako k dětem [...]."],
	# tohle je dobrej bizár
	"N-J-V": ["Dejte jí najevo svou ", bold, "lásku a chovejte", " se k ní něžně."],
	"N-Z-J-P-V": ["Mám pocit, ", bold, "že se chová", " davově a stádně."],
	"N-V": [bold, "Naději choval", " do poslední chvíle."],
	"N-Z-J-P-N-V": ["Máte ", bold, "pocit, že se policie chová", " nemravně?"],
	"N-Z-J-P-R-P-N-V": ["Máme k němu jiný ", bold, "vztah, nebo se ke každému vozu chováte", " stejně?"],
	"V-D-J-V-N": ["Navíc se vláda ", bold, "chovala zmateně a ztratila respekt", "."],
	"N-Z-D-P-V": ["S otcem jsem měla komplikované ", "vztahy, často se choval", " agresivně."],
	"V-D-Z-J-V-N": ["Lidé se mají ", bold, "chovat zásadově, ale nemít předsudky", ", říká se."],
	"N-Z-J-N-P-V": ["Hráči mají ", bold, "podezření, že hra se chová", " jako živá."],
	"N-Z-J-P-V-V": ["Máte ", bold, "pocit, že se umíme chovat", " k cizincům jako k sobě rovným?"]
}

examples_lemma = {
	"v/ve": [bold, "Chovám v sobě naději", "."],
	"k/ke": [bold, "Chovám k nim důvěru", "."],
	"vůči": [bold, "Nechováme vůči vám nenávist", "."],
	"proti": [bold, "Nechovám proti nikomu nenávist", "."],
	"pro": [bold, "Chováte pro něco vášeň", "?"],
	"o": [bold, "Nechová o sobě pražádné iluze", "."],
	"na": [bold, "Naději na zlepšení chová", " jen málokdo."],
	"od": ["Velmi jsem tuto stavbu obdivoval a ", bold, "chovám od té doby velký obdiv", " ke všemu."],
	"za": ["K protivníkovi je třeba ", bold, "chovat za všech okolností úctu", "."],
	"z": ["Předstírat nadšení, když k nim ", bold, "chováte z duše odpor", ", není v pořádku."],
	"před": ["Klatovské mužstvo ", bold, "chová před Jihočechy respekt", "."],
	"podle": ["K doktorce ", bold, "chová podle svých slov stejnou důvěru", " a vděčnost jako k doktorce Kaňkové."],
	"díky": ["K Čechám ", bold, "chovám díky nedávným angažmá silný vztah", "."]
}

antiexamples_lemma = {
	"v/ve": ["Žilková už v dětství měla ", bold, "potřebu v náruči chovat", " dítě. (N-R-N-V)"],
	"pro": ["Moje rodina žije na vesnici a pár slepiček jsme také ", bold, "chovali pro svou potřebu", ". (V-R-P-N)"],
	"od": ["Schopnost oddělovat osobní ", bold, "pocity od potřeby chovat",
		   " se jako manažer profesionálně. (N-R-N-V)"],
	"z": "",
	"k/ke": " ",
}

second_position = {
	"NN": "substantivum obyčejné",
	"AA": "adjektivum obyčejné",
	"AC": "jmenný tvar adjektiva",
	"AU": "adjektivum přivlastňovací (na „-ův“ i „-in“)",
	"AG": "adjektivum odvozené od slovesného tvaru přítomného přechodníku",
	"AM": "adjektivum odvozené od slovesného tvaru minulého přechodníku",
	"AO": "adjektiva „svůj“, „nesvůj“, „tentam“ (nezájmenné výrazy v přísudkové/doplňkové pozici)",
	"PP": "osobní zájmeno",

	"PH": ["krátký tvar osobního zájmena (", italic, "mě, mi, ti, mu", " …)"],
	"P5": ["zájmeno ", italic, "on, oni", " ve tvarech po předložce (tj. ", italic, "n-", ": ", italic,
		   "něj, něho, nich", " …)"],
	"P6": ["reflexivní zájmeno ", italic, "se", " v dlouhých tvarech (", italic, "sebe, sobě, sebou", ")"],
	"P7": ["reflexivní zájmeno ", italic, "se, si", " pouze v těchto tvarech, a dále ", italic, "ses, sis"],
	"PD": ["ukazovací zájmeno (", italic, "ten, onen", " …)"],
	"PS": ["přivlastňovací zájmeno ", italic, "můj, tvůj, jeho", " (vč. plurálu)"],
	"P8": ["přivlastňovací zájmeno ", italic, "svůj"],
	"P1": ["vztažné přivlastňovací zájmeno (", italic, "jehož, jejíž", " …)"],
	"PZ": ["neurčité zájmeno (", italic, "nějaký, některý, číkoli, cosi", " …)"],
	"PL": ["neurčité zájmeno ", italic, "všechen, sám"],
	"PW": ["záporné zájmeno (", italic, "nic, nikdo, nijaký, žádný", " …)"],
	"P4": ["vztažné nebo tázací zájmeno s adjektivním skloňováním (obou typů: ", italic, "jaký, který, čí", " …)"],
	"PJ": ["vztažné zájmeno ", italic, "jenž", " (", italic, "již", " …), bez předložky"],
	"P9": ["vztažné zájmeno ", italic, "jenž, již", " … po předložce (", italic, "n", "“: ", italic, "něhož, níž",
		   " …)"],
	"PK": ["tázací nebo vztažné zájmeno ", italic, "kdo", ", vč. tvarů s ", italic, "-ž", " a ", italic, "-s"],
	"PQ": ["tázací nebo vztažné zájmeno ", italic, "co, copak, cožpak"],
	"PE": ["vztažné zájmeno ", italic, "což"],
	"Cl": "číslovka základní 1–4 + „nejeden“",
	"Cn": "číslovka základní 5–99, i pokud je součástí složené číslovky psané dohromady („dvacetpět“, „stotřicet“, „pětapůl“)",
	"Cz": "číslovka základní se substantivním skloňováním („sto“, „milion“, „nula“ apod.)",
	"Ca": "číslovka základní neurčitá a tázací („mnoho“, „tolik“, „kolik“)",
	"Cy": "číslovka dílová („půl“, „polovic“, „polovina“)",
	"Cr": "číslovka řadová",
	"Cw": "číslovka řadová neurčitá a tázací",
	"Cd": "číslovka druhová a souborová („dvojí“, „obojí“, „čtverý“ včetně tvarů „dvoje“, „oboje“, „čtvery“; „obé“; „jedny“)",
	"Ch": "číslovka druhová a souborová neurčitá a tázací",
	"Cj": "číslovka úhrnná („čtvero“, „patero“, „devatero“, „dvé“, „tré“)",
	"Ck": "číslovka úhrnná neurčitá a tázací („několikero“, „tolikero“, „kolikero“)",
	"Cu": "číslovka násobná (adjektivní typ: „dvojitý“, „osminásobný“)",
	"C3": "číslovka násobná neurčitá a tázací (adjektivní typ: „mnohonásobný“, „xnásobný“, „kolikanásobný“)",
	"Cv": "číslovka násobná (adverbiální typ, včetně spřežek: „pětkrát“, „osminásobně“, „trojnásob“, „jednou“)",
	"Co": "číslovka násobná neurčitá a tázací (adverbiální typ, včetně spřežek: „mnohokrát“, „několikanásobně“, „pokolikáté“, „naponěkolikáté“ …)",
	"C=": "číslo psané arabskými číslicemi",
	"C}": "číslo psané římskými číslicemi",
	"Vf": "infinitiv",
	"VB": "tvar přítomného nebo budoucího času",
	"Vt": "archaický tvar přítomného nebo budoucího času (zakončení „-ť“)",
	"Vi": "tvar rozkazovacího způsobu",
	"Vc": "kondicionál slovesa být („by“, „bych“, „bys“, „bychom“, „byste“)",
	"Vp": "tvar minulého aktivního příčestí (včetně přidaného „-s“)",
	"Vq": "archaický tvar minulého aktivního příčestí (zakončení „-ť“)",
	"Vs": "tvar pasívního příčestí (vč. přidaného „-s“)",
	"Ve": "tvar přechodníku přítomného („-e“, „-íc“, „-íce“)",
	"Vm": "tvar přechodníku minulého, příp. (zastarale) přechodník přítomný dokonavý",
	"Dg": "příslovce (s určením stupně a negace; „velký“, „zajímavý“ …)",
	"Db": "příslovce (bez určení stupně a negace; „pozadu“, „naplocho“ …)",
	"RR": "předložka obyčejná",
	"RV": "předložka vokalizovaná („ve“, „pode“, „ku“ …)",
	"RF": "součást předložky, která nikdy nestojí samostatně („narozdíl“, „vzhledem“ …)",
	"J^": "spojka souřadicí",
	"J,": "spojka podřadicí (vč. „aby“ a „kdyby“ ve všech tvarech)",
	"J*": "spojka: operátor („plus“, „minus“, „x“)",
	"TT": "částice",
	"II": "citoslovce",
	"S2": "prefixoid (samostatně stojící předpona nebo předpona oddělená spojovníkem)",
	# "S[": "]	u sufixoidů se na druhé pozici vyskytují detailní určení jiných slovních druhů v závislosti na tom, k jakému slovu se sufixoid vztahuje",
	# "B[": "]	u zkratek se na druhé pozici vyskytují detailní určení jiných slovních druhů v závislosti na tom, jaké slovo zkratka zkracuje",
	"Z:": "interpunkce všeobecně",
	"Z0": "nekoncová interpunkce (tečka za zkratkou, číslicí apod.)",
	"F%": "cizí slovo",
	"X@": "morfologickou analýzou nerozpoznaný tvar",
	"Xx": "lovní druh neurčen/neznámý",
}

# Only POS
only_pos_rows = []
only_pos_columns = ["POS", "příklad", "APKS (%)", "vztažné", "jiné", "sort_by"]
total_vnp = sum(v[1] for k, v in data_working_pos.items())

for key_pos, value in data_working_pos.items():
	pos = key_pos.split("-")
	example = examples[key_pos] if key_pos in examples else ""
	n_vnp = value[1]
	only_pos_rows.append(
		[key_pos, example, prcnt_wrap(before=str(n_vnp) + " (", count=n_vnp, total=total_vnp), value[3], value[0],
		 n_vnp])
df_only_pos = pd.DataFrame(only_pos_rows, columns=only_pos_columns)
df_only_pos = df_only_pos.sort_values("sort_by", ascending=False)

only_pos_prcnt = 0;
only_pos_cumulative_coll = []
for index, row in df_only_pos.iterrows():
	only_pos_prcnt += prcnt(row["sort_by"], total_vnp)
	only_pos_cumulative_coll.append(str(round(only_pos_prcnt, 2)).replace(".", ","))

df_only_pos_exclude_vztazne = df_only_pos.drop("vztažné", axis=1)
df_only_pos_exclude_vztazne.insert(loc=3, column='APKS kumulativní %',
								   value=only_pos_cumulative_coll)  # https://stackoverflow.com/questions/18674064/how-do-i-insert-a-column-at-a-specific-column-index-in-pandas

# POS & POS with second position
pos_detailed_rows = []
pos_detailed_columns = ["POS", "POS + detail", "APKS", "vztažné", "jiné", "délka"]
for key_pos_detailed, value in data_working_pos_detailed.items():
	pos_detailed = key_pos_detailed.split("-")
	pos = get_pos_from_detailed(pos_detailed)
	pos_detailed_rows.append([pos, key_pos_detailed, value[1], value[3], value[0], len(pos_detailed)])
df_pos_detailed = pd.DataFrame(pos_detailed_rows, columns=pos_detailed_columns)
df_pos_detailed = df_pos_detailed.sort_values("APKS", ascending=False)

# POS & POS with second position - interested only in the middle
pos_detailed_simplified_rows = []
pos_detailed_simplified_columns = ["POS", "POS + detail", "APKS", "vztažné", "jiné", "délka"]
for key_pos_detailed_simplified, value in data_working_pos_detailed_simplified.items():
	pos_detailed_simplified = key_pos_detailed_simplified.split("-")
	pos = get_pos_from_detailed(pos_detailed_simplified)
	pos_detailed_simplified_rows.append(
		[pos, key_pos_detailed_simplified, value[1], value[3], value[0], len(pos_detailed_simplified)])
df_pos_detailed_simplified = pd.DataFrame(pos_detailed_simplified_rows, columns=pos_detailed_simplified_columns)
df_pos_detailed_simplified = df_pos_detailed_simplified.sort_values("APKS", ascending=False)

# Get first at_prcnt POS:
at = 0
at_sample_total = total_vnp * 0.80  # prvnich 80 procent
at_break = False
at_pos = {}
at_analyzed = []
for index, row in df_only_pos.iterrows():
	if not at_break:
		at_analyzed.append(row["POS"])
		pos = row["POS"].split("-")
		for p in pos:
			if p not in at_pos:
				at_pos[p] = 0
			at_pos[p] += row["sort_by"]
		at += row["sort_by"]  # count against percentage
		if at > at_sample_total:
			at_break = True

# Organize pattrns by second position
at_pos_d = {}
at_pos_d_counts = {}
for index, row in df_pos_detailed.iterrows():
	if row["POS"] in at_analyzed:
		pos_detailed = row["POS + detail"].split("-")
		for p_d in pos_detailed:
			if p_d not in at_pos_d:
				at_pos_d[p_d] = 0
				at_pos_d_counts[p_d] = {}
			at_pos_d[p_d] += row["APKS"]
			at_pos_d_counts[p_d][row["POS + detail"]] = row["APKS"]

# prepare rows
at_columns = ["POS", "2. pozice", "příklady", "celkem", "shrnutí"]
at_rows = []
at_pron_count = 0;
at_prep_count = 0;
for p, v in at_pos.items():
	for key, values in at_pos_d_counts.items():
		if key[0] == p:
			at_rows.append([p, key[1], second_position[key], at_pos_d[key], 1])
			if p == "P":
				at_pron_count += at_pos_d[key]
			if p == "R":
				at_prep_count += at_pos_d[key]
			for p_d, count in sorted(values.items(), key=lambda item: item[1], reverse=True):
				at_rows.append([p, key[1], p_d, count, 0])
df_at_pos = pd.DataFrame(at_rows, columns=at_columns)

# Zájmena v analyzovaném vzorku
pron_columns = ["detailní určení", "příklad", "APKS", "%", "sort_by"]
pron_rows = []
for index, row in df_at_pos.iterrows():
	if row["shrnutí"] == 1 and row["POS"] == "P":
		tag = row["POS"] + row["2. pozice"]
		pron_rows.append([second_position[tag], examples[tag], row["celkem"],
						  prcnt_wrap(row["celkem"], at_pron_count, before="", after=""), row["celkem"]])
df_pron = pd.DataFrame(pron_rows, columns=pron_columns)
df_pron = df_pron.sort_values("sort_by", ascending=False)

# Předložky v analyzovaném vzorku
prep_columns = ["předl.", "APKS (%)", "příklad", "jiné", "protipříklad", "sort_by"]
prep_rows = []
prep_data_is_vnp = count_lemmas(data_working_pos_prep_is_vnp, at_analyzed, "R")
prep_data_not_vnp = count_lemmas(data_working_pos_prep_not_vnp, at_analyzed, "R")
prep_total_is_vnp = sum(v for k, v in prep_data_is_vnp.items())
for lemma, count in prep_data_is_vnp.items():
	count_non_vnp = prep_data_not_vnp[lemma] if lemma in prep_data_not_vnp else 0
	example = examples_lemma[lemma] if lemma in examples_lemma else ""
	antiexample = antiexamples_lemma[lemma] if lemma in antiexamples_lemma else ""
	prep_rows.append(
		[lemma,  str(count) + prcnt_wrap(count, prep_total_is_vnp), example,count_non_vnp, antiexample,  count])

df_prep = pd.DataFrame(prep_rows, columns=prep_columns)
df_prep = df_prep.sort_values("sort_by", ascending=False)

# Ulož csv
# df_only_pos.to_csv(parent_directory + '/_data/pos.csv', sep=";", encoding="utf-8", index=False)
# print('✅ CSV uloženo')

df_only_pos = df_only_pos.drop("sort_by", axis=1)
df_only_pos_exclude_vztazne = df_only_pos_exclude_vztazne.drop("sort_by", axis=1)

df_pos_not_apks = df_only_pos.drop("vztažné", axis=1)
df_pos_not_apks = df_pos_not_apks.drop("APKS (%)", axis=1)
df_pos_not_apks = df_pos_not_apks.sort_values("jiné", ascending=False)

df_pron = df_pron.drop("sort_by", axis=1)
df_prep = df_prep.drop("sort_by", axis=1)

# Write each dataframe to a different worksheet.
df_only_pos_exclude_vztazne.to_excel(writer, sheet_name='POS', index=False)
df_only_pos.to_excel(writer, sheet_name='POS + vztažné', index=False)
df_pos_not_apks.to_excel(writer, sheet_name='POS jiné', index=False)
df_pos_detailed.to_excel(writer, sheet_name='POS + 2', index=False)
df_pos_detailed_simplified.to_excel(writer, sheet_name='POS + 2 (simpl)', index=False)
df_at_pos.to_excel(writer, sheet_name='POS2 analysis', index=False)
df_pron.to_excel(writer, sheet_name='POS2 pron', index=False)
df_prep.to_excel(writer, sheet_name='lemma prep', index=False)

# Close the Pandas Excel writer and output the Excel file.
writer.save()
print('✅ Excel uložen')
