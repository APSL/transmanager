# -*- encoding: utf-8 -*-

from django.core.management.base import BaseCommand
from transmanager.models import TransModelLanguage
from transmanager.tasks.tasks import create_translations_for_item_and_its_children


class Command(BaseCommand):
    help = "Generate the translation tasks from the existing data."

    def handle(self, *args, **options):

        self.stdout.write('Start')
        # generate the translations tasks for every record on the translatable models
        for model in TransModelLanguage.objects.all():
            mc = model.get_model_class()
            self.stdout.write('Model: {}'.format(mc.__name__))
            for item in mc.objects.all():
                self.stdout.write('{} - Item: {}'.format(mc.__name__, item.pk))
                create_translations_for_item_and_its_children.delay(mc, item.pk)
        self.stdout.write('End')

