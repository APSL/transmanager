# -*- encoding: utf-8 -*-

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.http import HttpResponse
from django.views.generic import ListView, UpdateView
from django_yubin.messages import TemplatedHTMLEmailMessageView

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from api2.weblogitravel.views import BaseViewMixin
from transmanager.export import ExportQueryset
from transmanager.serializers import TaskBulksSerializer
from .models import TransTask
from .forms import TaskForm
from .filters.filters import TaskFilter
from .permissions import AuthenticationMixin


class TaskListView(AuthenticationMixin, ListView):
    # extends = 'cms/dashboard.html'
    extends = 'dashboard.html'
    model = TransTask
    template_name = "list.html"
    paginate_by = 25
    filter = None

    def get_default_values(self):
        data = self.request.GET.copy()
        data.update({'record_status': self.request.GET.get('record_status', 'not_translated')})
        return data

    def get_queryset(self):
        qs = super().get_queryset()
        if self.translator_user:
            qs = qs.filter(user=self.translator_user)
        self.filter = TaskFilter(self.get_default_values(), queryset=qs, user=self.translator_user)
        return self.filter

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['filter'] = self.filter
        data['total'] = self.filter.count()
        data['words'] = self.filter.qs.aggregate(number=Sum('number_of_words'))
        return data

    def get(self, request, *args, **kwargs):
        if request.GET.get('export', False):
            qs = self.get_queryset()
            export = ExportQueryset(qs, self.model, ('id', 'object_name', 'object_pk',
                                                     'object_field_label', 'object_field_value', 'number_of_words',
                                                     'object_field_value_translation', 'date_modification', 'done'))
            excel = export.get_excel()
            response = HttpResponse(excel, content_type='application/xls')
            response['Content-Disposition'] = 'attachment;filename=export.xls'
            return response
        return super().get(request, *args, **kwargs)


class TaskDetailView(AuthenticationMixin, UpdateView):
    extends = 'dashboard.html'
    model = TransTask
    form_class = TaskForm
    template_name = 'detail.html'

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


class TaskBulksView(BaseViewMixin, APIView):

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
