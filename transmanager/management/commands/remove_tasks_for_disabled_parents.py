# -*- encoding: utf-8 -*-

from django.core.management.base import BaseCommand
from transmanager.models import TransModelLanguage
from transmanager.settings import TM_DEFAULT_ENABLED_ATTRIBUTE_NAME
from transmanager.tasks.tasks import delete_translations_for_item_and_its_children
from transmanager.utils import has_field


class Command(BaseCommand):
    help = "Removes the tasks belonging to a deactivated parents."

    def handle(self, *args, **options):

        filter_by = {
            TM_DEFAULT_ENABLED_ATTRIBUTE_NAME: False
        }

        whole_ids = []

        self.stdout.write('Start')
        # generate the translations tasks for every record on the translatable models
        for model in TransModelLanguage.objects.all():
            mc = model.get_model_class()
            if not has_field(mc, TM_DEFAULT_ENABLED_ATTRIBUTE_NAME):
                continue

            # if the model has the enabled attr, the we search the disabled items ids
            disabled_ids = list(mc.objects.filter(**filter_by).values_list('id', flat=True))
            whole_ids += disabled_ids
            self.stdout.write('Model: {} has {} ids'.format(mc.__name__, len(disabled_ids)))
            if disabled_ids:
                for item_id in disabled_ids:
                    delete_translations_for_item_and_its_children.delay(mc, item_id)

        self.stdout.write('{} ids will be processed'.format(len(whole_ids)))

        self.stdout.write('End')
