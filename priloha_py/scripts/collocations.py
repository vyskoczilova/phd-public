import pandas as pd

from scripts.helpers import Helpers


class Collocations():

	def __init__(self, source_csv):
		self.df = None
		self.src = source_csv
		self.load()

	def load(self):
		self.df = pd.read_csv(self.src, sep=";", index_col=0, dtype=str, keep_default_na=False)
		self.df = self.df.reset_index()
		n_order = []
		order = 1
		for index, row in self.df.iterrows():
			if row["POS"] == "N":
				n_order.append(str(order) + ".")
				order += 1
			else:
				n_order.append("")
		self.df["N order"] = n_order

	def getLogDiceScore(self, lemma):
		values = self.df[self.df['lemma'] == lemma]['logDice'].tolist()
		return values[0]

	def getNOrder(self, lemma):
		values = self.df[self.df['lemma'] == lemma]['N order'].tolist()
		return values[0]
