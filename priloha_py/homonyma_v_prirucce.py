from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import InvalidSessionIdException
import re
import sys
import argparse

#######################
#   Enter your data   #
#######################

# List of nouns in nominative case - to be searched in prirucka.ujc.cas.cz
data_source = ["akce", "aktivita", "analýza", ]

# The of a word to which homonyms will be searched for.
data_case = 4

#################################
#   Script itself starts here   #
#################################


class PriruckaResults:
	def __init__(self, word, info="OK"):
		self.word = word
		self.info = info
		self.grammatical_number = "sg"
		self.homonyms_count = 0
		self.homonyms_cases = []
		self.others_count = 0
		self.others_notes = []

	def setGrammaticalNumber(self, grammatical_number):
		self.grammatical_number = grammatical_number

	def setHomonymsCases(self, homonyms_cases):
		self.homonyms_count = len(homonyms_cases)
		self.homonyms_cases = homonyms_cases

	def setOthersNotes(self, others_notes):
		self.others_count = len(others_notes)
		self.others_notes = others_notes

	def isError(self):
		return True if self.info != "OK" else False

	def getData(self):
		return self.word + "\t" + self.info + "\t" + self.grammatical_number + "\t" + str(
			self.homonyms_count) + "\t" + ", ".join(self.homonyms_cases) + "\t" + str(
			self.others_count) + "\t" + "; ".join(self.others_notes)


# Get word by case from grammatial number paradigm.
def get_word_by_case(grammatical_number, case_number):
	for idx, case in enumerate(grammatical_number):
		if idx != case_number - 1:
			continue

		if isinstance(case, WebElement):
			if hasattr(case, "text"):
				return get_all_word_forms(case.text)

		return case


# Get homonymous forms from selected grammatial number paradigm.
def match_keyword_in_grammatical_numbers(grammatical_number, keyword, suffix=""):
	cases = ["N", "G", "D", "A", "V", "L", "I"]
	same_forms = []

	if len(grammatical_number) != len(cases):
		return False

	for idx, case in enumerate(grammatical_number):
		if isinstance(case, WebElement):
			word_forms = get_all_word_forms(case.text)
		else:
			word_forms = case
		for word_form in word_forms:
			if word_form == keyword:
				same_forms.append(cases[idx] + suffix)
	return same_forms


# Cleanup word from unwanted characters and split to words.
def get_all_word_forms(string):
	# Remove footnotes.
	string = re.sub(r'[0-9]+', '', string)
	array = string.split(", ")
	return array


def processResuts(singular, plural, keyword, status="OK"):
	same_forms = []
	same_forms_singular = match_keyword_in_grammatical_numbers(singular, keyword, "sg")
	same_forms_plural = match_keyword_in_grammatical_numbers(plural, keyword, "pl")

	# Not passing example: "odvolání" (odpovolat)
	if same_forms_singular != False or same_forms_plural != False:
		same_forms += same_forms_singular
		same_forms += same_forms_plural

	# Example: "odpovědnost" (zodpovědnost)
	if not same_forms:
		return PriruckaResults(keyword, "manual")
	else:
		prirucka = PriruckaResults(keyword, status)
		prirucka.setHomonymsCases(same_forms)
		return prirucka


# Search selected word in prirucka.ujc.cas.cz.
def get_cases_with_same_word_form(keyword, driver, get_case=False):
	url = "https://prirucka.ujc.cas.cz/?slovo=" + keyword
	other_meanings = []

	driver.get(url)

	# Check if it is a noun or also another POS
	# Examples: "vinu" (vina, vinout, víno), "naději" (naděje, nadát se, nadít se)
	if not driver.find_elements_by_css_selector(".para"):
		return PriruckaResults(keyword, "not found")
	# add other entries note
	trs = driver.find_elements_by_css_selector("#dalsiz tr")

	if not trs:
		links = []

		for tr in trs:
			other_meanings.append(tr.text)
			if tr.text.find("pád") >= 0:

				link = tr.find_elements_by_css_selector("a")
				if link[0]:
					links.append(link[0].get_attribute("href"))

		# If only one noun, load the page, otherwise return
		if len(links) == 1:
			driver.get(links[0])
		elif len(links) > 1:
			return PriruckaResults(keyword, "manual")

	# load singular and plural forms

	singular = driver.find_elements_by_css_selector(".para tr .centrovane:not(.width7):nth-child(2)")
	plural = driver.find_elements_by_css_selector(".para tr .centrovane:not(.width7):nth-child(3)")
	status = "OK"

	# Fix deverbal nouns
	if len(singular) == 9 and len(plural) == 5:
		status = "deverbal noun"
		is_deverbal_noun = True
		singular = [[keyword], [keyword], [keyword], [keyword], [keyword], [keyword], [keyword + "m"]]
		plural = [[keyword], [keyword], [keyword + "m"], [keyword], [keyword], [keyword + "ch"], [keyword + "mi"]]

	# other entries
	trs = driver.find_elements_by_css_selector("#dalsiz tr")
	for tr in trs:
		if tr.text.lower() == keyword:
			continue
		other_meanings.append(tr.text)

	# Hanle another possible edge case aka not found
	if not singular or not plural:
		return [PriruckaResults(keyword, "error")]

	if get_case:

		if is_deverbal_noun:
			return [singular[get_case - 1], plural[get_case - 1]]

		singular_keywords = get_word_by_case(singular, get_case)
		plural_keywords = get_word_by_case(plural, get_case)
		return [singular_keywords, plural_keywords]

	results = processResuts(singular, plural, keyword, status)
	results.setOthersNotes(other_meanings)
	return results


# Get selected case in singular and plural form.
def get_sg_pl(keyword, case, driver):
	# get singular and plural forms
	singular_plural = get_cases_with_same_word_form(keyword, driver, case)
	# check if singular_plural is dictionary
	if not isinstance(singular_plural, list):
		print(keyword + "\t" + singular_plural.getData())
		return []
	return singular_plural


# Prepare Chrome browser
# https://stackoverflow.com/questions/64927909/failed-to-read-descriptor-from-node-connection-a-device-attached-to-the-system
# https://stackoverflow.com/questions/60296873/sessionnotcreatedexception-message-session-not-created-this-version-of-chrome

browser = webdriver.Chrome(ChromeDriverManager().install())

# Lookup word forms in příručka UJČ and expect it to be a noun
for word in data_source:
	# word: str = "ústup"
	singular_plural_forms = get_sg_pl(word, data_case, browser)

	# no data → skip
	if len(singular_plural_forms) == 0:
		continue

	for sg in singular_plural_forms[0]:
		info = get_cases_with_same_word_form(sg, browser)
		info.setGrammaticalNumber("sg")
		print(word + "\t" + info.getData())

	for pl in singular_plural_forms[1]:
		info = get_cases_with_same_word_form(pl, browser)
		info.setGrammaticalNumber("pl")
		print(word + "\t" + info.getData())

# Close the browser
browser.close()
