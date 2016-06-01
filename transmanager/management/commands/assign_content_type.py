# -*- encoding: utf-8 -*-

import logging
import concurrent.futures

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from transmanager.models import TransTask

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Assign the content type to the task"
    num_workers = 25

    @staticmethod
    def proces_task(task):
        app_label = task.object_name.split(' - ')[0]
        model = task.object_class.lower()
        ct = ContentType.objects.get_by_natural_key(app_label, model)
        task.content_type = ct
        task.save()
        return task.id

    def handle(self, *args, **options):

        self.stdout.write('Start')

        processed, processed_errors = 0, 0
        qs = TransTask.objects.all()

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            future_ref = {executor.submit(self.proces_task, item): item for item in qs}
            for future in concurrent.futures.as_completed(future_ref):
                item_processed = future_ref[future]
                try:
                    data_result = future.result()
                except Exception as exc:
                    self.stdout.write('{} exception: {}'.format(item_processed.id, exc))
                    processed_errors += 1
                else:
                    processed += 1
                    self.stdout.write('Processed {}'.format(data_result))

        self.stdout.write('Total processed: {}'.format(processed))
        self.stdout.write('Total with errors: {}'.format(processed_errors))
        self.stdout.write('End')
