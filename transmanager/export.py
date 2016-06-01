# -*- encoding: utf-8 -*-

from datetime import datetime
from io import BytesIO
from xlsxwriter.workbook import Workbook


class ExportQueryset(object):
    """
    Utility to export querysets to excel
    """
    def __init__(self, qs, model, columns):
        self.qs = qs
        self.model = model
        self.columns = columns

    def get_excel(self):
        output = BytesIO()
        excel = Workbook(output)
        sheet = excel.add_worksheet()

        # write header
        for num_col, column in enumerate(self.columns):
            sheet.write(0, num_col, self.get_field_name(column))

        # write data tuples
        for num_row, item in enumerate(self.qs, start=1):
            for num_col, column in enumerate(self.columns):
                value = getattr(item, column, '')
                if not value:
                    value = ''
                if isinstance(value, (bool, datetime)):
                    value = str(value)
                sheet.write(num_row, num_col, value)

        # close the excel file
        excel.close()
        return output.getvalue()

    def get_field_name(self, field):
        try:
            return self.model._meta.get_field_by_name(field)[0].verbose_name
        except Exception:
            return ''
