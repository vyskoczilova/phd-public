from scripts.helpers import prcnt, prcnt_wrap
from statistics import mean, mode


class Data:
	def __init__(self, cql_type):
		self.type = cql_type
		self.ostatni = 0
		self.vnp = 0
		self.vztazne = 0
		self.neurceno = 0
		self.total = 0
		self.wordcounts_vnp = []

	def __getitem__(self, key):
		return getattr(self, key)

	def __setitem__(self, key, value):
		return setattr(self, key, value)

	def setTotal(self, total):
		self.total = total

	def add(self, where, add=1):
		self.__validateWhere(where)
		self[where] += add

	def __validateWhere(self, where):
		if where not in ["ostatni", "vnp", "vztazne", "neurceno"]:
			print("Chyba - " + where + " neexistuje")
			quit()

	def getType(self):
		return self.type

	def getTotal(self):
		return self.total if self.total != 0 else self.ostatni + self.vnp + self.vztazne + self.neurceno

	def getTotalPercentage(self, total):
		return prcnt(self.getTotal(), total)

	def getTotalWithPercentage(self, total):
		return str(self.getTotal()) + prcnt_wrap(self.getTotal(), total)

	def getCounts(self, where):
		self.__validateWhere(where)
		return self[where]

	def getPercentage(self, where):
		self.__validateWhere(where)
		return prcnt(self[where], self.getTotal())

	def getCountsWithPercentage(self, where, total = None):
		self.__validateWhere(where)
		if total is None:
			total = self.getTotal()
		return str(self[where]) + prcnt_wrap(self[where], total)

	def getWordcounts(self):
		return self.wordcounts_vnp

	def getWordcountsStatistics(self):
		# get unique values
		list_set = set(self.wordcounts_vnp)
		unique_list = (list(list_set))
		statistics = {}

		for x in unique_list:
			statistics[x] = self.wordcounts_vnp.count(x)

		# sort by key
		statistics = dict(sorted(statistics.items(), key=lambda item: item[0]))
		return statistics

	def getWordcountsMin(self):
		return min(self.wordcounts_vnp) if len(self.wordcounts_vnp) else ''

	def getWordcountsMax(self):
		return max(self.wordcounts_vnp) if len(self.wordcounts_vnp) else ''

	def getWordcountsMean(self):
		return round(mean(self.wordcounts_vnp), 2) if len(self.wordcounts_vnp) else ''

	def getWordcountsMode(self):
		return mode(self.wordcounts_vnp) if len(self.wordcounts_vnp) else ''

	def getCountsVnpVztazne(self):
		return self.getCounts("vnp") + self.getCounts("vztazne")

	def getPercentageVnpVztazne(self):
		return prcnt(self.getCountsVnpVztazne(), self.getTotal())

	def getCountsWithPercentageVnpVztazne(self):
		return str(self.getCountsVnpVztazne()) + prcnt_wrap(self.getCountsVnpVztazne(), self.getTotal())


class DataLemmas(Data):
	def __init__(self, lemma, cql_type):
		self.lemma = lemma
		self.lemma_accepted = False
		super().__init__(cql_type)

	def getLemma(self):
		return self.lemma + "*" if self.lemma_accepted else self.lemma

	def setAcceptedAlready(self):
		self.lemma_accepted = True

	def addWordcount(self, wordcount):
		self.wordcounts_vnp.append(wordcount - 2)


class DataTypes(Data):

	def addWordCounts(self, wordcounts):
		self.wordcounts_vnp = self.wordcounts_vnp + wordcounts
