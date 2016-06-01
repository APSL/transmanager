# -*- encoding: utf-8 -*-

from django.core.management.base import BaseCommand
from ...models import TransTask
from ...utils import get_num_words


class Command(BaseCommand):
    help = "Update the number of words of the tasks"

    def handle(self, *args, **options):
        self.stdout.write('Reading tasks...')
        pairs = []
        for it in TransTask.objects.all():
            pairs.append({'id': it.id, 'num': get_num_words(it.object_field_value)})

        for item in pairs:
            TransTask.objects.filter(pk=item['id']).update(number_of_words=item['num'])

        self.stdout.write('end')

