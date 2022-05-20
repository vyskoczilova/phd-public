import re
import requests
from bs4 import BeautifulSoup

class VallexQuest():

	def __init__(self, verb):
		self.verb = verb
		self.lemma = ""
		self.lemma2 = []
		self.all_boxes = []
		self.soup_v4 = None

	def load(self):
		self.__search_in_v4()
		self.__get_lemma()
		self.__get_all()

	# Retrieve HTML from Vallex
	def __search_in_v4(self):
		response = requests.get(
		'https://quest.ms.mff.cuni.cz/cgi-bin/vallex/frame-search-result.pl?directory=data_release-4.0&lexeme_lemmas='+self.verb+'&frame=CPHR&v-vallex&delcomment&output=lexemes&whole_forms&highlighting=color&show_file&show_lexeme_lemmas&show_frame_lemmas&show_frame&show_synon&show_example&show_class&show_control&show_use&show_note&show_id&show_pdt-vallex&show_otherforms&show_specval&show_type&show_shortform&show_status&show_full&show_lvc&show_map&show_instig')
		self.soup_v4 = BeautifulSoup(
			response.content.decode('utf-8'), features="html.parser")

	def __get_lemma(self, where_soup = None):
		if where_soup == None:
			where_soup = self.soup_v4
		lemma = where_soup.find('b', attrs={'class': 'lemma'}).text
		self.lemma = re.findall("\* (.*)", lemma)[0].lower()

	def __get_all(self, where_soup = None):
		if where_soup == None:
			where_soup = self.soup_v4

		lemmas = []
		boxes = where_soup.div.find_all('div', attrs={'class': 'box'})

		for box in boxes:
			lemma2 = box.find('b', attrs={'class': 'lemma2'}).text
			lemmas.append(lemma2)
			self.all_boxes.append(box.text)

		self.lemma2 = list(set(lemmas))

	def get_meaning(self):
		synon = []
		for box in self.all_boxes:
			if "lvc:" in box:
				continue
			s = re.findall('-synon: (.*)', box)
			u = re.findall('-use: (.*)', box)
			synon.append(s)
		return synon

# https://github.com/muniperez/wrapapi-post-processing-scripts/blob/master/portos-hidrovias-para.js
