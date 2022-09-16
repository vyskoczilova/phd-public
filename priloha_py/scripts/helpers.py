import os
import re
from os import listdir
from os.path import join, isdir
import pandas as pd
import czech_sort


def prcnt(count, total):
	return round((count / total) * 100, 2)


def prcnt_wrap(count, total, before=" (", after=")"):
	return before + str(prcnt(count, total)).replace(".", ",") + after


def merge_prep_lemmas(lemma):
	if lemma == "k" or lemma == "ke":
		lemma = "k/ke"
	elif lemma == "v" or lemma == "ve":
		lemma = "v/ve"
	return lemma


def unique_sort_list(data):
	return sorted(list(set(data)), key=czech_sort.key)


def get_vnp_dict(directory, value="1"):
	vnps = []
	file = Helpers.csv_file_starts_with(directory, "anotovano")
	if file:
		df = pd.read_csv(directory + '/' + file, sep=";", index_col=0, dtype=str, keep_default_na=False)
		df = df.reset_index()
		for index, row in df.iterrows():
			if row["VNP?"] == value:
				vnps.append(row["lemma"])
	return sorted(list(set(vnps)), key=czech_sort.key)


def get_pos_from_detailed(detailed):
	pos = []
	for d in detailed:
		pos.append(d[0])
	return '-'.join(str(x) for x in pos)


def replace_in_list(data, search, replace):
	updated = []
	for item in data:
		updated.append(item.replace(search, replace))
	return updated



class Helpers:

	@staticmethod
	def csv_file_starts_with(directory, starts_with):
		if os.path.isdir(directory):
			pattern = re.compile(starts_with + ".*\\.csv$")
			for file in os.listdir(directory):
				if pattern.match(file):
					return file
		return False

	@staticmethod
	def get_list_of_annotated_files(parent_directory, exclude_directories=['old', 'test', "_data"], files_to_load=["N-V_anotovano.csv", "V-N_anotovano.csv"]):
		directories = [name for name in listdir(parent_directory) if
					   isdir(join(parent_directory, name)) and name not in exclude_directories]
		files = []
		for file in directories:
			source_directory = join(parent_directory, file)
			for f in listdir(source_directory):
				if f in files_to_load:
					files.append(source_directory + "/" + f)
		return files


class Annotate:
	def __init__(self, directory):
		self.files = Helpers.get_list_of_annotated_files(directory)
		self.lemma = []
		self.pos = []
		self.pos_detailed = []
		self.grammatical_gender = []
		self.__load_information()

	def __load_information(self):
		for file in self.files:
			df = pd.read_csv(file, sep=";", index_col=0, dtype=str, keep_default_na=False)
			df = df.reset_index()

			for index, row in df.iterrows():
				sentence = row["left"] + " " + row["kwic"] + " " + row["right"]
				words = sentence.split()
				pos_regex = re.compile(r'[^/]*/([^/]*)/(.)(.)(.)')
				for word in words:
					find = re.findall(pos_regex, word)
					if find:
						lemma = find[0][0]
						if lemma not in self.lemma:
							self.lemma.append(lemma)
							self.pos.append(find[0][1])
							self.pos_detailed.append(find[0][2])
							self.grammatical_gender.append(find[0][3])

	def get_pos(self, lemma):
		if lemma in self.lemma:
			index = self.lemma.index(lemma)
			return self.pos[index]
		return ""
