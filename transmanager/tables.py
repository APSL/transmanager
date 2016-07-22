# -*- encoding: utf-8 -*-

import django_tables2 as tables

from django.utils import text
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django_tables2.utils import Accessor
from .settings import TM_ORIGINAL_VALUE_CHARS_NUMBER
from .models import TransTask


class TaskTable(tables.Table):

    detail = tables.Column(accessor=Accessor('pk'), verbose_name=' ')

    class Meta:
        model = TransTask
        fields = ('user', 'language', 'object_name', 'object_pk', 'object_field_label', 'object_field_value',
                  'number_of_words', 'date_creation', 'date_modification', 'done', 'detail')
        empty_text = _('No se han encontrado resultados')
        attrs = {'class': 'table table-bordered table-hover table-condensed', 'id': 'taskList'}
        template = 'table.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'request' in kwargs:
            self.GET = kwargs['request'].GET
        else:
            self.GET = None

    def render_object_field_value(self, record, value):
        return text.Truncator(value).chars(TM_ORIGINAL_VALUE_CHARS_NUMBER, html=True)

    def render_detail(self, record, value):
        url = reverse('transmanager-task-detail', kwargs={'pk': record.id})
        if self.GET:
            return mark_safe('<a href="{0}?{1}">'
                             '<i class="fa fa-pencil-square-o" aria-hidden="true"></i> '
                             '</a>'.format(url, self.GET.urlencode()))
        else:
            return mark_safe('<a href="{0}">'
                             '<i class="fa fa-pencil-square-o" aria-hidden="true"></i> '
                             '</a>'.format(url))
