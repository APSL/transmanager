# -*- encoding: utf-8 -*-

import django_filters
from django.contrib.contenttypes.models import ContentType
from django.forms.widgets import Select
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel

from transmanager.models import TransUser, TransLanguage, TransTask, TransModelLanguage


class TaskFilter(django_filters.FilterSet):

    RECORDS_TYPES = (
        ('', _('Todos')),
        ('modified', _('Modificados')),
        ('not_modified', _('No modificados')),
    )

    RECORD_STATUS = (
        ('', _('Todos')),
        ('translated', _('Traducidos')),
        ('not_translated', _('No traducidos'))
    )

    usuario = django_filters.ModelChoiceFilter(queryset=TransUser.objects.all(), required=False,
                                               label=_('Usuario'), field_name='user')

    content_type = django_filters.ChoiceFilter(choices=(), required=False, label=_('Clase'))

    language = django_filters.ModelChoiceFilter(queryset=TransLanguage.objects.order_by('name'), required=False,
                                                label=_('Idioma'))

    record_status = django_filters.CharFilter(
        label=_('Estado'), widget=Select(choices=RECORD_STATUS), required=False, method='filter_record_status')

    record_types = django_filters.CharFilter(
        label=_('Tipo registro'), widget=Select(choices=RECORDS_TYPES), method='filter_record_types'
    )

    object_pk = django_filters.NumberFilter(required=False, label=_('Clave'))

    dates = django_filters.DateFromToRangeFilter(label=_('Rango de fechas'), required=False, field_name='date_modification')

    class Meta:
        model = TransTask
        fields = ('usuario', 'language', 'content_type', 'record_types', 'record_status', 'object_pk', 'dates')

    @staticmethod
    def filter_record_status(queryset, name, value):
        if value == 'translated':
            return queryset.extra(
                where=["object_field_value_translation IS NOT NULL AND object_field_value_translation !=''"]
            )
        elif value == 'not_translated':
            return queryset.extra(
                where=["object_field_value_translation IS NULL OR object_field_value_translation =''"]
            )
        return queryset

    @staticmethod
    def filter_record_types(queryset, name, value):
        if value == 'modified':
            return queryset.extra(
                where=["to_char(date_creation, 'YY-MM-DD HH24:MI')!=to_char(date_modification, 'YY-MM-DD HH24:MI')"]
            )
        elif value == 'not_modified':
            return queryset.extra(
                where=["to_char(date_creation, 'YY-MM-DD HH24:MI')=to_char(date_modification, 'YY-MM-DD HH24:MI')"]
            )
        return queryset

    @staticmethod
    def filter_object_field_label(queryset, value):
        if not value:
            return queryset
        obj_class, obj_field = value.split('__')
        return queryset.filter(object_class=obj_class, object_field=obj_field)

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None, user= None):
        super().__init__(data, queryset, request=request, prefix=prefix)
        self.filters['content_type'].extra['choices'] = self.get_choices_for_models()

        if not user:
            return

        del self.filters['usuario']
        languages = user.languages.all()
        if languages:
            num = languages.count()
            if num > 1:
                self.filters['language'].extra['queryset'] = languages
            elif num == 1:
                del self.filters['language']

    @staticmethod
    def get_choices_for_models():
        """
        Get the select choices for models in optgroup mode
        :return:
        """
        result = {}

        apps = [item.model.split(' - ')[0] for item in TransModelLanguage.objects.all()]
        qs = ContentType.objects.exclude(model__contains='translation').filter(app_label__in=apps).order_by(
            'app_label', 'model'
        )
        for ct in qs:
            if not issubclass(ct.model_class(), TranslatableModel):
                continue
            if ct.app_label not in result:
                result[ct.app_label] = []
            result[ct.app_label].append((
                ct.id, str(ct.model_class()._meta.verbose_name_plural)
            ))
        choices = [(str(_('Todas las clases')), (('', _('Todas las clases')),))]
        for key, value in result.items():
            choices.append((key, tuple([it for it in sorted(value, key=lambda el: el[1])])))
        return choices
