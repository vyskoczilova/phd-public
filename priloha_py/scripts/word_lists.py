import os

class WordLists:

	def __init__(self):
		self.lists = []

	# Load file with words separated by new lines
	def loadWordList(self, file, origin):
		words = []
		if os.path.isfile(file):
			with open(file, "r", encoding='utf-8') as list_file:
				for word in list_file:
					words.append(word.strip())
			list_file.close()
		self.lists.append({origin: words})

	# Search word in dictionary and returns origin
	def search(self, word):
		for list in self.lists:
			for key in list:
				for w in list[key]:
					if w == word:
						return key
		return False
