# -*- encoding: utf-8 -*-

from django.core.management.base import BaseCommand
from transmanager.models import TransTask, TransUser
from transmanager.views import TaskUserNotificationView


class Command(BaseCommand):
    help = "Command that notifies the translators of pending translation tasks."

    def handle(self, *args, **options):

        self.stdout.write('Start')

        # obtain all the users that have pending tasks
        users = TransUser.objects.filter(
            pk__in=TransTask.objects.values('user').filter(done=False).order_by('user').distinct()
        )

        # generate a notification with the last 50 pending tasks for each user
        for user in users:
            self.stdout.write('Email: {}'.format(user.user.email))
            TaskUserNotificationView(
                tasks=user.tasks.filter(done=False).order_by('-id')[:50],
                user=user
            ).send(to=(user.user.email,))

        self.stdout.write('End')
