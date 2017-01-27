# -*- encoding: utf-8 -*-

from django.contrib import messages
from django.contrib.sites.models import Site
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.views.generic import UpdateView, FormView, TemplateView
from django.shortcuts import HttpResponseRedirect, HttpResponse
from django.views.generic.detail import BaseDetailView
from django_tables2 import SingleTableView, RequestConfig
from django_yubin.messages import TemplatedHTMLEmailMessageView
from haystack.query import SearchQuerySet

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .tables import TaskTable
from .serializers import TaskBulksSerializer
from .models import TransTask, TransUserExport
from .forms import TaskForm, UploadTranslationsForm
from .filters.filters import TaskFilter
from .permissions import AuthenticationMixin
from .settings import TM_ORIGINAL_VALUE_CHARS_NUMBER, TM_HAYSTACK_DISABLED, TM_HAYSTACK_SUGGESTIONS_MAX_NUMBER
from .tasks.tasks import import_translations_from_excel, export_translations_to_excel


class TaskListView(AuthenticationMixin, SingleTableView):
    extends = 'dashboard.html'
    model = TransTask
    template_name = "list.html"
    paginate_by = 25
    filter = None
    table_class = TaskTable

    def get_table(self, **kwargs):
        kwargs['request'] = self.request
        table_class = self.get_table_class()
        table = table_class(self.get_table_data(), **kwargs)
        RequestConfig(self.request, paginate=self.get_table_pagination(table)).configure(table)
        return table

    def get_default_values(self):
        data = self.request.GET.copy()
        data.update({'record_status': self.request.GET.get('record_status', 'not_translated')})
        return data

    def get_queryset(self):
        qs = super().get_queryset()
        if self.translator_user:
            qs = qs.filter(user=self.translator_user)
        self.filter = TaskFilter(self.get_default_values(), queryset=qs, user=self.translator_user)
        return self.filter.qs

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['filter'] = self.filter
        data['total'] = self.filter.count()
        data['words'] = self.filter.qs.aggregate(number=Sum('number_of_words'))
        data['original_value_max_chars'] = TM_ORIGINAL_VALUE_CHARS_NUMBER
        return data

    def get(self, request, *args, **kwargs):

        if request.GET.get('export', False):
            tasks_ids = self.get_queryset().values_list('id', flat=True)
            export_translations_to_excel.delay(tasks_ids, self.request.user.id)
            messages.info(
                self.request,
                _('Iniciado el proceso de exportación de traducciones.\nSe notificará al usuario una vez concluído')
            )
            return HttpResponseRedirect(reverse('transmanager-message'))

        return super().get(request, *args, **kwargs)


class TaskDetailView(AuthenticationMixin, UpdateView):
    extends = 'dashboard.html'
    model = TransTask
    form_class = TaskForm
    template_name = 'detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not TM_HAYSTACK_DISABLED:
            sqs = SearchQuerySet().filter(content=self.object.object_field_value).\
                filter(language=self.object.language).filter(has_value=True)
            context['sqs'] = sqs[:TM_HAYSTACK_SUGGESTIONS_MAX_NUMBER]
            context['obj_id'] = str(self.object.id)
        return context

    def get_success_url(self):
        url = '{}?{}'.format(reverse('transmanager-task-list'), self.request.GET.urlencode())
        return url

    def get_initial(self):
        initial = super().get_initial()

        app_label = self.object.object_name.split('-')[0].strip()
        obj_type = ContentType.objects.get(app_label=app_label, model=self.object.object_class.lower())
        model_class = obj_type.model_class()

        try:
            item = model_class.objects.language(self.object.language.code).get(pk=self.object.object_pk)
            initial.update({'object_field_value_translation': getattr(item, self.object.object_field)})
        except ObjectDoesNotExist:
            pass
        return initial


class MessageView(AuthenticationMixin, TemplateView):
    """
    View that holds the message window
    """
    template_name = 'message.html'


class UploadTranslationsView(FormView):
    """
    View that allow the user upload an excel with translations and update the translations tasks
    """
    form_class = UploadTranslationsForm
    template_name = 'upload-translations.html'

    def form_valid(self, form):
        import_translations_from_excel.delay(form.cleaned_data['file'], self.request.user.id)
        messages.info(
            self.request,
            _('Iniciado el proceso de importación de traducciones.\nSe notificará al usuario una vez concluído')
        )
        return HttpResponseRedirect(reverse('transmanager-message'))


class DownloadFileView(BaseDetailView):
    """
    View used to download the file exported by the user
    """
    model = TransUserExport
    slug_url_kwarg = 'uuid'
    slug_field = 'uuid'

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user_id != self.request.user.id and not self.is_superuser:
            raise Http404
        response = HttpResponse(obj.file.read(), content_type='application/xls')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(obj.file.name)
        return response

    @property
    def is_superuser(self):
        return self.request.user.is_superuser


class TaskUserNotificationView(TemplatedHTMLEmailMessageView):
    """
    View used to define the notification of translation pending task to the translators.
    """
    subject_template_name = 'notification/subject.txt'
    body_template_name = 'notification/body.txt'
    html_body_template_name = 'notification/body.html'

    def __init__(self, tasks, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tasks = tasks
        self.user = user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = self.tasks
        context['user'] = self.user
        return context


class ImportExportNotificationView(TemplatedHTMLEmailMessageView):
    """
    View used to notificate the user the end of the importation process
    """
    subject_template_name = 'notification/import_export_notification_subject.txt'
    body_template_name = 'notification/import_export_notification_body.txt'
    html_body_template_name = 'notification/import_export_notification_body.html'

    def __init__(self, user, errors=None, user_export=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.user_export = user_export
        self.errors = errors

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site = Site.objects.get_current()
        context['domain_url'] = 'http://{}'.format(site.domain)
        context['user'] = self.user
        context['user_export'] = self.user_export
        context['errors'] = self.errors
        return context


# @todo resolve permission to post/delete to the API
# class TaskBulksView(AuthenticationMixin, APIView):
class TaskBulksView(APIView):
    """
    Handles the bulk addtion of translation tasks
    POST creates translations
    DELETE deletes translations
    ---
    # YAML

    POST:
        parameters:
            - name: app_label
              description: identifier of the application
              type: string
              required: true
              paramType: post
            - name: model
              description: model class in lowercase
              type: string
              required: true
              paramType: post
            - name: languages
              description: list of language codes to create/delete the tasks from (at least one)
              type: list
              required: true
              paramType: post
            - name: ids
              description: list of models id's from which create/delete the translation tasks (at least one)
              type: list
              required: true
              paramType: post

        request_serializer: transmanager.serializers.TaskBulksSerializer
        response_serializer: transmanager.serializers.TransTaskSerializer

    """
    serializer_class = TaskBulksSerializer

    def post(self, request):

        serializer = TaskBulksSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_404_NOT_FOUND)

        try:
            return Response(data=serializer.save(), status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(data=str(e), status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):

        serializer = TaskBulksSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_404_NOT_FOUND)

        try:
            return Response(data=serializer.delete(), status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data=str(e), status=status.HTTP_400_BAD_REQUEST)