# -*- encoding: utf-8 -*-
from optparse import make_option

import xlsxwriter
from hvad.utils import get_translation
from xlsxwriter.utility import xl_rowcol_to_cell
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from hvad.models import TranslatableModel
from transmanager.models import TransLanguage


class Command(BaseCommand):

    """
    DONE 1.- doblar fila per nou idioma
    DONE 2.- fixar el nom de la classe
    DONE 3.- comptar i mostrar núm. paraules
    DONE 4.- totalitzar núm. paraules per columna
    DONE 5.- totalitzar núm. paraules per fila total final
    DONE 6.- Demanar com a paràmetre el nom de l'aplicació a exportar
    DONE 7.- Demanar com a paràmetre l'idioma destí a exportar
    DONE 8.- Filtrar només els registres que no tenen traducció en l'idioma destinació
    DONE 9.- Afegir fulla de totals
    DONE 10.- Implementar protecció de les fulles. només són editables les cel.les on hi van les traduccions
    """

    help = "Command for the export text duty"

    option_list = BaseCommand.option_list + (
        make_option(
            "-a",
            "--app",
            dest="app_label",
            help="specify app name. E.g: Transfers, Golf, ...",
            metavar="APP"
        ),
    )

    option_list = option_list + (
        make_option(
            "-l",
            "--lang",
            dest="destination_lang",
            help="specify destination lang",
            metavar="DESTINATION_LANG"
        ),
    )

    @staticmethod
    def _get_main_language():
        """
        returns the main language
        :return:
        """
        try:
            main_language = TransLanguage.objects.filter(main_language=True).get()
            return main_language.code
        except TransLanguage.DoesNotExist:
            return 'es'

    def _get_translated_field_names(self, instance):
        translated_field_names = set(instance._translated_field_names) - set(self._get_internal_fields())
        return translated_field_names

    @staticmethod
    def _get_internal_fields():
        hvad_internal_fields = ['id', 'language_code', 'master', 'master_id']
        return hvad_internal_fields

    def fields_need_translation(self, elem, destination_lang):
        """
        Detect if the tuple needs translation and which fields has to be translated
        :param elem
        :param destination_lang:
        :return:
        """

        fields = self._get_translated_field_names(elem)
        elem_langs = elem.get_available_languages()
        # if we don't have a translation for the destination lang we have to include the tuple
        if destination_lang not in elem_langs:
            return fields

        # we have the translation, we decide which fields we need to translate. we have to get the translation first
        translation = get_translation(elem, destination_lang)
        result = []
        for field in fields:
            value = getattr(translation, field, '')
            if not value or value.strip() == '':
                result.append(field)

        return result

    def handle(self, *args, **options):

        if not options['app_label']:
            raise CommandError("Option `--app=...` must be specified.")

        if not options['destination_lang']:
            raise CommandError("Option `--lang=...` must be specified. E.g.: (en, de, fr, it, pt, fi)")

        app_label = options['app_label']
        destination_lang = options['destination_lang']
        main_lang = self._get_main_language()
        sheets = []

        # obtain the metadata for the app
        items = ContentType.objects.filter(app_label=app_label).all()
        for item in items:
            cls = item.model_class()
            if not isinstance(cls(), (TranslatableModel, )):
                continue
            self.stdout.write('Model: {}'.format(cls()._meta.verbose_name_plural))
            fields = sorted(list(self._get_translated_field_names(cls())))
            fields.insert(0, 'main_lang')
            fields.insert(0, 'id')

            self.stdout.write('{}'.format(cls().__class__.__name__))

            sheets.append({
                'name': '{}'.format(cls()._meta.verbose_name_plural),
                'class': cls,
                'class_name': '{}'.format(cls().__class__.__name__),
                'fields': fields
            })

        # create the excel file
        wb = xlsxwriter.Workbook('{0}_{1}.xlsx'.format(app_label, destination_lang))
        ini_row, ini_col = 2, 1

        # add formats
        bold = wb.add_format({'bold': True})
        number = wb.add_format({'num_format': '#', 'bold': True, 'locked': True})
        bold_right = wb.add_format({'bold': True, 'align': 'right', 'locked': True})
        already_translated_field = wb.add_format({'color': '#ff0000', 'locked': True})
        # unlocked = wb.add_format({'locked': False})
        # locked = wb.add_format({'locked': True})

        ws_total = wb.add_worksheet('Totales')
        ws_total.set_column(1, 1, 30)
        ws_total.set_column(2, 2, 13)
        # ws_total.protect()

        row_total, row_total_init = 2, 2
        col_total = 1
        ws_total.write(row_total, col_total, 'Modelo', bold)
        ws_total.write(row_total, col_total + 1, 'Nº palabras', bold_right)
        row_total += 1

        for sheet in sheets:
            row, col = ini_row, ini_col

            # sheet title
            ws = wb.add_worksheet(sheet['name'])
            # ws.protect()
            ws.write(row, ini_col, sheet['class_name'], bold)
            row += 1

            ws.write(row, ini_col, sheet['name'], bold)
            row += 2
            col = ini_col

            max_col_widths = {}

            # fields header
            for field_name in sheet['fields']:
                ws.write(row, col, field_name, bold)
                col += 1
                if field_name not in ['id', 'main_lang']:
                    ws.write(row, col, 'num_words', bold_right)
                    col += 1
                    max_col_widths[field_name] = {'col': None, 'width': 0}

            row += 2

            data_init_row = 7
            totalize_columns = []

            # tuples
            # rows
            found = False
            for elem in sheet['class'].objects.language(main_lang).order_by('pk'):

                # if all the fields are already translated in the destination language then avoid this tuple
                fields_to_translate = self.fields_need_translation(elem, destination_lang)
                if len(fields_to_translate) == 0:
                    continue

                # at least there is one item
                found = True

                # self.stdout.write('{}, {}'.format(elem.id, elem_langs))

                # cols
                col = ini_col
                for field in sheet['fields']:
                    if field == 'main_lang':
                        # lang field
                        ws.write(row, col, main_lang)
                    elif field == 'id':
                        # id field
                        ws.write(row, col, getattr(elem, 'id'))
                    else:
                        # text fields
                        value = getattr(elem, field)
                        if field in fields_to_translate:
                            ws.write(row, col, value)
                            ws.write(row + 1, col, '')
                        else:
                            ws.write(row, col, value, already_translated_field)

                        # ample col.
                        max_col_widths[field]['col'] = col
                        if value and len(value) > max_col_widths[field]['width']:
                            max_col_widths[field]['width'] = len(value)

                        col += 1
                        if isinstance(value, (str, )):
                            if field in fields_to_translate:
                                ws.write_number(row, col, len(value.split()) if value else 0)
                            else:
                                ws.write_number(row, col, 0, already_translated_field)
                            if col not in totalize_columns:
                                totalize_columns.append(col)
                    col += 1

                row += 1
                col = ini_col

                # translation row
                ws.write(row, col, getattr(elem, 'id'))
                col += 1
                ws.write(row, col, destination_lang)
                row += 2

            if not found:
                continue

            # fix cols width
            for k, v in max_col_widths.items():
                self.stdout.write('setting width for {0},{0} to {1} for {2}'.format(v['col'], int(int(v['width'] * 1.3)), sheet['name']))
                ws.set_column(v['col'], v['col'], int(int(v['width']) * 1.3))
                ws.set_column(v['col'] + 1, v['col'] + 1, 13)

            # totalize sheet
            ws.write(row, ini_col, 'Total', bold_right)
            gran_total_row = row
            gran_total_col = max(totalize_columns)
            gran_total_ini_cell = xl_rowcol_to_cell(gran_total_row, ini_col)
            gran_total_end_cell = xl_rowcol_to_cell(gran_total_row, gran_total_col)
            for col in totalize_columns:
                init_cell = xl_rowcol_to_cell(data_init_row, col)
                end_cell = xl_rowcol_to_cell(row-2, col)
                ws.write_formula(row, col, '{{=SUM({}:{})}}'.format(init_cell, end_cell), number)
            # sum of all the words of all the columns of the sheet
            ws.write_formula(gran_total_row, gran_total_col + 2, '{{=SUM({}:{})}}'.format(gran_total_ini_cell,
                                                                                          gran_total_end_cell), number)

            # save in the totalize sheet
            cell = xl_rowcol_to_cell(gran_total_row, gran_total_col + 2)
            ws_total.write(row_total, col_total, sheet['name'])
            ws_total.write_formula(row_total, col_total+1, "{{'{0}'!{1}}}".format(sheet['name'], cell), number)
            row_total += 1

            # end of the sheet
            self.stdout.write('end sheet {}'.format(sheet['name']))

        g_total_ini_cell = xl_rowcol_to_cell(row_total_init, col_total + 1)
        g_total_end_cell = xl_rowcol_to_cell(row_total, col_total + 1)

        row_total += 1
        ws_total.write(row_total, col_total, 'Total', bold_right)
        ws_total.write_formula(row_total, col_total+1,
                               '{{=SUM({}:{})}}'.format(g_total_ini_cell, g_total_end_cell), number)

        self.stdout.write('end workbook')
