import csv
import os
import re
from scripts.helpers import Helpers
# https://pypi.org/project/colorama/
from colorama import Fore, Back, Style, init


class Concordance():

	def __init__(self, sourceDir):
		self.directory = './' + sourceDir
		self.concordance = []

	# Load concordance file and parse the data.
	def parse_concordance(self, start_pattern="^kontext-conc"):
		if os.path.isdir(self.directory):
			file = Helpers.csv_file_starts_with(self.directory, start_pattern);
			if file:
				with open(self.directory + '/' + file, "r", encoding='utf-8') as concordance_file:
					concordance_rows = csv.reader(concordance_file, delimiter=';')
					next(concordance_rows)
					next(concordance_rows)
					for row in concordance_rows:
						self.concordance.append(ConcordanceRow(row[1], row[2], row[3]))
					concordance_file.close()

	# Search lemma in KWIC and print selected number of examples
	def print_examples_from_kwic(self, lemma, number_of_examples):
		i = 0
		for row in self.concordance:
			if row.kwic_has_lemma(lemma, True) and i < number_of_examples:
				print(row.get_sententce(True))
				i += 1


class ConcordanceRow:

	def __init__(self, left, kwic, right):
		self.left = left if isinstance(left, str) else ""
		self.kwic = kwic if isinstance(kwic, str) else ""
		self.right = right if isinstance(right, str) else ""
		self.kwic_pos = None
		self.kwic_pos_detailed = None
		self.pos = ["N", "A", "P", "C", "V", "D", "R", "J", "T", "I", "S", "B", "Z", "F",
					"X"]  # https://wiki.korpus.cz/doku.php/seznamy:tagy#pozice_1_-_slovni_druh

	def __getitem__(self, key):
		return getattr(self, key)

	# Strip lemmas from text
	def strip_lemma_and_tag(self, concordance_part, keep_last=False):
		if self[concordance_part]:
			words = self[concordance_part].split()
			cleaned = ""
			if len(words):
				last_word = words.pop()
				for word in words:
					cleaned += re.sub('/[^/]*', '', word) + ' '
				if keep_last:
					cleaned += last_word + ' '
				else:
					cleaned += re.sub('/[^/]*', '', last_word) + ' '
				return cleaned
		else:
			return ''

	# Strip lemmas from text
	def strip_verbtag_from(self, concordance_part):
		if self[concordance_part]:
			words = self[concordance_part].split()
			cleaned = []
			nonverbtag_regex = re.compile(r'([^/]*/[^/]*/[^/]*)/.*')
			if len(words):
				for word in words:
					find = re.findall(nonverbtag_regex, word)
					cleaned.append(find[0])

				return " ".join(cleaned)
		else:
			return ''

	# Clean spaces and others.
	def __lint_text(self, string):
		string = string.replace(' .', '.')
		string = string.replace(' ,', ',')
		string = string.replace(' !', '!')
		string = string.replace(' ?', '?')
		string = string.replace('( ', '(')
		string = string.replace(' )', ')')
		string = string.replace('„ ', '„')
		string = string.replace('“ ', '“')
		string = string.replace('  ', ' ')
		return string

	# Get whole sentence with possibly colored KWIC.
	def get_sententce(self, color=False):
		init()
		sentence = self.strip_lemma_and_tag('left')
		if color:
			sentence += Fore.RED
		sentence += self.strip_lemma_and_tag('kwic')
		if color:
			sentence += Fore.RESET
		sentence += self.strip_lemma_and_tag('right')
		return self.__lint_text(sentence)

	# Kwic contains lemma?
	def kwic_has_lemma(self, lemma, last_word_only=False):
		if last_word_only:
			last_word = self.kwic.strip().split(sep=" ").pop()
			if "/" + lemma + "/" in last_word:
				return True
		elif "/" + lemma + "/" in self.kwic:
			return True
		return False

	def kwic_get_lemmas(self):
		words = self.kwic.split()
		lemmas = []
		lemma_regex = re.compile(r'[^/]*/([^/]*)/.*')
		for word in words:
			find = re.findall(lemma_regex, word)
			lemmas.append(find[0])
		return lemmas

	def kwic_get_verbtags(self):
		words = self.kwic.split()
		vertbtags = []
		verbtag_regex = re.compile(r'[^/]*/[^/]*/[^/]*/(.*)')
		for word in words:
			find = re.findall(verbtag_regex, word)
			vertbtags.append(find[0])
		return vertbtags

	def kwic_get_pos(self):
		if self.kwic_pos is not None:
			return self.kwic_pos
		pos = []
		if self.kwic:
			words = self.kwic.split()
			pos_regex = re.compile(r'[^/]*/[^/]*/(.)')
			for word in words:
				find = re.findall(pos_regex, word)
				pos.append(find[0])
		self.kwic_pos = pos
		return pos

	def kwic_get_pos_detailed(self):
		if self.kwic_pos_detailed is not None:
			return self.kwic_pos_detailed
		pos = []
		if self.kwic:
			words = self.kwic.split()
			pos_regex = re.compile(r'[^/]*/[^/]*/(..)')
			for word in words:
				find = re.findall(pos_regex, word)
				pos.append(find[0])
		self.kwic_pos_detailed = pos
		return pos

	def kwic_get_pos_formatted(self):
		pos = self.kwic_get_pos()
		return '-'.join(str(x) for x in pos)

	def kwic_get_pos_detailed_formatted(self):
		pos = self.kwic_get_pos_detailed()
		return '-'.join(str(x) for x in pos)

	def kwic_get_pos_detailed_formatted_simplified(self):
		pos_detailed_formatted = self.kwic_get_pos_detailed_formatted()
		return pos_detailed_formatted[0:1] + pos_detailed_formatted[2:-1]

	# Match single pattern kwic
	def kwic_pos_has_pattern(self, pattern):
		pos = self.kwic_get_pos()
		if pos == pattern:
			return True
		return False

	# Match several patterns kwic
	def kwic_pos_has_patterns(self, patterns):
		for pattern in patterns:
			matches = self.kwic_pos_has_pattern(pattern)
			if matches:
				return True
		return False

	def kwic_contains_word(self, word):
		if " " + word + "/" in self.kwic:
			return True
		return False

	def kwic_matches_pos_or_word(self, matches):
		words = self.strip_lemma_and_tag("kwic").split()
		if len(words) != len(matches):
			return False
		if self.kwic_pos is None:
			self.kwic_get_pos()
		for idx, m in enumerate(matches):
			if m in self.pos:
				if self.kwic_pos[idx] != m:
					return False
			else:
				if words[idx] != m:
					return False
		return True

	def kwic_match_end_pos_or_word(self, matches):
		words = self.strip_lemma_and_tag("kwic").split()
		last_x = len(matches)
		last_words = words[-last_x:]
		if self.kwic_pos is None:
			self.kwic_get_pos()
		last_pos = self.kwic_pos[-last_x:]
		for idx, m in enumerate(matches):
			if m in self.pos:
				if last_pos[idx] != m:
					return False
			else:
				if last_words[idx] != m:
					return False
		return True

	def right_starts_with_word(self, word):
		return self.right.startswith(word + '/')

	def verb_negation(self):
		verb_index = self.kwic_get_pos().index("V")
		words = self.strip_lemma_and_tag('kwic').split()
		lemmas = self.kwic_get_lemmas()
		if words[verb_index][0:2] == "ne" and (lemmas[verb_index][0:2] != "ne" or words[verb_index][0:4] == "nene"):
			return True
		return False

	def get_nouns_number(self):
		words = self.kwic.split()
		if "NN" in words[0]:
			noun = words[0]
		else:
			noun = words[-1]
		noun_tag = noun.split("/")[2]
		return noun_tag[3]


class POS:
	def __init__(self):
		self.first = {
			"N": "substantivum (podstatné jméno)",
			"A": "adjektivum (přídavné jméno)",
			"B": "zkratka",
			"C": "numerál (číslovka, nebo číselný výraz s číslicemi)",
			"D": "adverbium (příslovce)",
			"F": "cizí slovo",
			"I": "interjekce (citoslovce)",
			"J": "konjunkce (spojka)",
			"P": "pronomen (zájmeno)",
			"R": "prepozice (předložka)",
			"S": "segment",
			"T": "partikule (částice)",
			"V": "verbum (sloveso)",
			"X": "neznámý, neurčený, neurčitelný slovní druh",
			"Z": "interpunkce, hranice věty",
		}
		self.second = {
			"NN": "substantivum obyčejné",
			"AA": "adjektivum obyčejné",
			"AC": "jmenný tvar adjektiva",
			"AU": "adjektivum přivlastňovací (na „-ův“ i „-in“)",
			"AG": "adjektivum odvozené od slovesného tvaru přítomného přechodníku",
			"AM": "adjektivum odvozené od slovesného tvaru minulého přechodníku",
			"AO": "adjektiva „svůj“, „nesvůj“, „tentam“ (nezájmenné výrazy v přísudkové/doplňkové pozici)",
			"PP": "osobní zájmeno",
			"PH": "krátký tvar osobního zájmena („mě“, „mi“, „ti“, „mu“ …)",
			"P5": "zájmeno „on“, „oni“ ve tvarech po předložce (tj. „n-“: „něj“, „něho“, „nich“ …)",
			"P6": "reflexivní zájmeno „se“ v dlouhých tvarech („sebe“, „sobě“, „sebou“)",
			"P7": "reflexivní zájmeno „se“, „si“ pouze v těchto tvarech, a dále „ses“, „sis“",
			"PD": "ukazovací zájmeno („ten“, „onen“ …)",
			"PS": "přivlastňovací zájmeno „můj“, „tvůj“, „jeho“ (vč. plurálu)",
			"P8": "přivlastňovací zájmeno „svůj“",
			"P1": "vztažné přivlastňovací zájmeno („jehož“, „jejíž“ …)",
			"PZ": "neurčité zájmeno („nějaký“, „některý“, „číkoli“, „cosi“ …)",
			"PL": "neurčité zájmeno „všechen“, „sám“",
			"PW": "záporné zájmeno („nic“, „nikdo“, „nijaký“, „žádný“ …)",
			"P4": "vztažné nebo tázací zájmeno s adjektivním skloňováním (obou typů: „jaký“, „který“, „čí“ …)",
			"PJ": "vztažné zájmeno „jenž“ („již“ …), bez předložky",
			"P9": "vztažné zájmeno „jenž“, „již“ … po předložce („n-“: „něhož“, „níž“ …)",
			"PK": "tázací nebo vztažné zájmeno „kdo“, vč. tvarů s „-ž“ a „-s“",
			"PQ": "tázací nebo vztažné zájmeno „co“, „copak“, „cožpak“",
			"PE": "vztažné zájmeno „což“",
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
