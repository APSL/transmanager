# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url
from .views import TaskListView, TaskDetailView, TaskBulksView

urlpatterns = patterns(
    '',
    url(r'^/task/$', TaskListView.as_view(), name='transmanager-task-list'),
    url(r'^/task/(?P<pk>\d+)/$', TaskDetailView.as_view(), name='transmanager-task-detail'),
    url(r'^/api/task/$', TaskBulksView.as_view(), name='transmanager-task-bulks'),
)
