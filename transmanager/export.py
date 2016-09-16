# -*- encoding: utf-8 -*-

import logging
import xlrd
from datetime import datetime
from io import BytesIO
from xlsxwriter.workbook import Workbook
from .models import TransTask

logger = logging.getLogger(__name__)


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


class ExportBo(object):
    """
    Class that encapsulates the task of exporting the translations taks to an excel file
    """

    @staticmethod
    def export_translations(tasks_ids):
        qs = TransTask.objects.filter(pk__in=tasks_ids)
        export = ExportQueryset(
            qs,
            TransTask,
            ('id', 'object_name', 'object_pk', 'object_field_label', 'object_field_value', 'number_of_words',
             'object_field_value_translation', 'date_modification', 'done')
        )
        excel = export.get_excel()
        return excel


class ImportBo(object):
    """
     Class that encapsulated the task of importing all the translations from an excel file
    """

    @staticmethod
    def import_translations(file):

        logger.info('Start of importing translations process')

        wb = xlrd.open_workbook(file_contents=file.read())
        sheet = wb.sheets()[0]
        init_data_row, id_col, translation_col = 1, 0, 6
        errors = []

        # proces every row and store it as a dict
        for row in range(init_data_row, sheet.nrows):

            task_id = int(sheet.cell_value(row, id_col))
            translation_value = sheet.cell_value(row, translation_col)
            if not translation_value or translation_value.strip() == '':
                continue

            try:
                logger.info('Updating: {} with: {}'.format(task_id, translation_value))
                task = TransTask.objects.get(pk=task_id)
                task.object_field_value_translation = translation_value
                task.date_modification = datetime.now()
                task.done = True
                task.save(update_fields=['done', 'date_modification', 'object_field_value_translation'])
            except TransTask.DoesNotExist:
                logger.info('Task {} not found'.format(task_id))
            except Exception as e:
                errors.append(str(e))

        logger.info('End of importing translations process')

        return errors
