import pandas as pd

#######################
#   Enter your data   #
#######################

# CSV with data to be processed
data_source = "cleaned_data.csv"

# Delimiter
data_delimiter = ","

#################################
#   Script itself starts here   #
#################################

# Load cleaned_data.csv in Pandas
df = pd.read_csv(data_source, sep=delimiter, encoding="utf-8")
df = df.reset_index()

count_homonym_cases = {}
homonym_types = {}

for index, row in df.iterrows():
	homonym_case = row["počet h. tvarů"]
	homonym_type = row["homonymní tvary"]

	if homonym_case not in count_homonym_cases.keys():
		count_homonym_cases[homonym_case] = 0
	if homonym_type not in homonym_types.keys():
		homonym_types[homonym_type] = 0

	count_homonym_cases[homonym_case] += 1
	homonym_types[homonym_type] += 1

count_homonym_cases = dict(sorted(count_homonym_cases.items()))

print(count_homonym_cases)

print()
print(homonym_types)

for key, value in homonym_types.items():
	print()
	print("tvary " + str(len(key.split(","))))
	print(key)
	print(value)
