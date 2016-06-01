# -*- encoding: utf-8 -*-

import sys
import datetime
import xlrd

from optparse import make_option
from hvad.utils import get_translation
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from transmanager.models import TransLanguage, TransTask

from django.db.models import Lookup
from django.db.models.fields import Field


class Lower(Lookup):
    """
    Custom lookup for postgres "lower" function implementation
    """

    lookup_name = 'lower'

    def as_sql(self, qn, connection):

        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return 'lower({}) = {}'.format(lhs, rhs), params

Field.register_lookup(Lower)


class Command(BaseCommand):

    """
    DONE 1.- llegir fulles
    DONE 2.- llegir cada registre
    DONE 3.- actualitzar el model
    DONE 4.- mirar si hi ha tasca de traducció per aquell registre, si existeix actualitzar-la i posar-la com a done
    """

    help = "Command for the import translations duty"

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

    def handle(self, *args, **options):

        if not options['app_label']:
            raise CommandError("Option `--app=...` must be specified.")

        if not options['destination_lang']:
            raise CommandError("Option `--lang=...` must be specified. E.g.: (en, de, fr, it, pt, fi)")

        app_label = options['app_label']
        destination_lang = options['destination_lang']
        main_lang = self._get_main_language()

        try:
            wb = xlrd.open_workbook('{}_{}.xlsx'.format(app_label, destination_lang))
        except Exception as e:
            self.stdout.write('Error: {}'.format(str(e)))
            sys.exit()

        sheets = wb.sheets()

        header_row = 5
        init_data_row = 7
        init_data_col = 1

        # result container
        result = {}

        ####################
        # parse excel data #
        ####################

        # we parse every sheet on the workbook
        for sh in sheets:

            # if no content then skip this sheet
            if sh.nrows == (header_row + 1) or sh.name.lower() == 'totales':
                continue

            # get the class name
            class_name = sh.cell_value(2, 1).lower()
            result[class_name] = []

            self.stdout.write('=' * 100)
            self.stdout.write('sheet: {} - {} - rows {} - cols {}'.format(sh.name, class_name, sh.nrows, sh.ncols))

            # proces every row and save it as a dict
            for row in range(init_data_row, sh.nrows - 2, 3):
                row_data = {'id': int(sh.cell_value(row, init_data_col))}
                col = init_data_col + 2
                while col <= sh.ncols-4:
                    row_data[sh.cell_value(header_row, col)] = sh.cell_value(row + 1, col)
                    col += 2
                result[class_name].append(row_data)

        # self.stdout.write('result: {}'.format(result))

        ###############
        # create data #
        ###############
        for class_name, data in result.items():
            model = ContentType.objects.filter(app_label=app_label, model=class_name).get()
            cls = model.model_class()

            for row in data:
                try:
                    item = cls.objects.language(main_lang).get(pk=row['id'])
                except cls.DoesNotExist:
                    continue
                try:
                    trans = get_translation(item, destination_lang)
                except Exception:
                    trans = item.translate(destination_lang)
                for field, value in row.items():
                    if field == 'id':
                        continue
                    setattr(trans, field, value)
                trans.save()

                ############################
                # update translation tasks #
                ############################
                for field, value in row.items():
                    if field == 'id' or value == '':
                        continue
                    try:
                        task = TransTask.objects.filter(
                            object_class__lower=class_name,
                            object_pk=row['id'],
                            language=TransLanguage.objects.filter(code=destination_lang).get(),
                            object_field=field
                        ).get()
                        task.object_field_value_translation = value
                        task.date_modification = datetime.datetime.now()
                        task.done = True
                        task.save(update_fields=['done', 'date_modification', 'object_field_value_translation'])
                    except TransTask.DoesNotExist:
                        pass

        # end
        self.stdout.write('=' * 100)
        self.stdout.write('end')
