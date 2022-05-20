import os
import csv


class CsvFile():

	def __init__(self, path):
		self.path = path
		self.headers = []
		self.rows = []
		self.number_of_lines = None

	def load_with_headers(self, delimiter=";"):
		if os.path.isfile(self.path):
			with open(self.path, "r", encoding='utf-8') as input_file:
				csv_reader = csv.reader(input_file, delimiter=delimiter)
				i = 0
				# Procházet jednotlivé řádky
				for row in csv_reader:
					if i == 0:
						self.headers = row
					else:
						data = {}
						ii = 0
						while ii < len(row):
							# Načti jen, pokud hlavička existuje
							if row[ii]:
								data[self.headers[ii]] = row[ii]
							# else:
							#  	print("Chyba na záznamu s ID " + row[0] + " sloupec číslo " + str(ii) + " chybí")
							ii += 1
						self.rows.append(data)
					i += 1
				self.number_of_lines = i

	def select_where_column_value(self, column, value, select_columns=None):
		if select_columns is None:
			select_columns = []
		return_statement = {}
		for row in self.rows:
			if row[column] == value:
				for sv in select_columns:
					return_statement[sv] = row.get(sv, "")
		return return_statement
