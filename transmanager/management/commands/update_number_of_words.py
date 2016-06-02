# -*- encoding: utf-8 -*-

from queue import Queue, Empty
from threading import Thread

from django.core.management.base import BaseCommand
from ...models import TransTask
from ...utils import get_num_words


class Command(BaseCommand):
    help = "Update the number of words to translate in every task"

    queue = Queue()
    num_threads = 80
    threads = []

    def handle(self, *args, **options):
        self.queue = Queue()
        self.stdout.write('Reading tasks...')
        for it in TransTask.objects.all():
            self.queue.put({'id': it.id, 'num': get_num_words(it.object_field_value)})

        for i in range(self.num_threads):
            t = Thread(target=self.worker_elements)
            t.start()
            self.threads.append(t)
        self.stdout.write("Waiting for empty queue")
        self.queue.join()
        self.stop_threads()

    def stop_threads(self):
        for t in self.threads:
            t.join()
        self.stdout.write('Exiting main thread')

    def worker_elements(self):
        while not self.queue.empty():
            try:
                item = self.queue.get(timeout=2)
                TransTask.objects.filter(pk=item['id']).update(number_of_words=item['num'])
            except Empty:
                break
            finally:
                self.queue.task_done()
