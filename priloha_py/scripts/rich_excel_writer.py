import xlsxwriter, pandas as pd
# https://devdreamz.com/question/129769-write-pandas-dataframe-to-excel-with-xlsxwriter-and-include-write-rich-string
from pandas.io.excel._xlsxwriter import XlsxWriter


class RichExcelWriter(XlsxWriter):
	def __init__(self, *args, **kwargs):
		super(RichExcelWriter, self).__init__(*args, **kwargs)

	def _value_with_fmt(self, val):
		if type(val) == list:
			return val, None
		return super(RichExcelWriter, self)._value_with_fmt(val)

	def write_cells(self, cells, sheet_name=None, startrow=0, startcol=0, freeze_panes=None):
		sheet_name = self._get_sheet_name(sheet_name)
		if sheet_name in self.sheets:
			wks = self.sheets[sheet_name]
		else:
			wks = self.book.add_worksheet(sheet_name)
			# add handler to the worksheet when it's created
			wks.add_write_handler(list, lambda worksheet, row, col, list, style: worksheet._write_rich_string(row, col,
																											  *list))
			self.sheets[sheet_name] = wks
		super(RichExcelWriter, self).write_cells(cells, sheet_name, startrow, startcol, freeze_panes)

# USAGE:
#
# writer = RichExcelWriter('pandas_with_rich_strings_class.xlsx')
# workbook  = writer.book
# bold = workbook.add_format({'bold': True})
# italic = workbook.add_format({'italic': True})
# red = workbook.add_format({'color': 'red'})
# df = pd.DataFrame({
#     'numCol': [1, 50, 327],
#     'plainText': ['plain', 'text', 'column'],
#     'richText': [
#         ['This is ', bold, 'bold'],
#         ['This is ', italic, 'italic'],
#         ['This is ', red, 'red']
#     ]
# })
#
# df.to_excel(writer, sheet_name='Sheet1', index=False)
#
# writer.save()
