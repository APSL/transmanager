# -*- encoding: utf-8 -*-

from django.urls import path
from .views import TaskListView, TaskDetailView, TaskBulksView, UploadTranslationsView, MessageView, DownloadFileView

urlpatterns = [
    path('/task/', TaskListView.as_view(), name='transmanager-task-list'),
    path('/task/<int:pk>/', TaskDetailView.as_view(), name='transmanager-task-detail'),
    path('/api/task/', TaskBulksView.as_view(), name='transmanager-task-bulks'),
    path('/upload-translations/', UploadTranslationsView.as_view(), name='transmanager-upload-translations'),
    path('/message/', MessageView.as_view(), name='transmanager-message'),
    path('/download-file/<uuid:uuid>/', DownloadFileView.as_view(), name='transmanager-download-file'),
]
