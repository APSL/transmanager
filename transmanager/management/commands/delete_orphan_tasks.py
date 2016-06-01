# -*- encoding: utf-8 -*-

import logging
from queue import Queue
from threading import Lock

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from ...models import TransTask, TransLanguage

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = "Mark translations tasks that have a translation value as done " \
           "and remove the tasks that does not have a parent anymore."

    lock = Lock()
    queue = Queue()
    num_threads = 40
    threads = []

    def handle(self, *args, **options):

        # remove tasks that don't have a parent anymore
        no_parent_total = 0
        logger.info('STEP 1 - Delete tasks that does not have a parent anymore')
        main_language = TransLanguage.objects.filter(main_language=True).get()
        for task in TransTask.objects.exclude(language=main_language).all():
            if not self.has_parent(task):
                logger.info('{} has NO parent'.format(task.id))
                task.delete()
                no_parent_total += 1
        logger.info('Deleted {} tasks with no parent'.format(no_parent_total))

    @staticmethod
    def has_parent(task):
        app_label, _ = task.object_name.split(' - ')
        model = task.object_class.lower()

        try:
            item = ContentType.objects.get_by_natural_key(app_label, model)
            model_class = item.model_class()
            try:
                model_class.objects.untranslated().use_fallbacks().filter(pk=task.object_pk).get()
                return True
            except (AttributeError, ObjectDoesNotExist):
                return False
        except ContentType.DoesNotExist:
            return False
