# -*- encoding: utf-8 -*-

from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from transmanager.forms import TransModelLanguageAdminForm, TransApplicationLanguageAdminForm
from transmanager.tasks.tasks import create_translations_for_item_and_its_children, \
    delete_translations_for_item_and_its_children
from .models import TransTask, TransUser, TransLanguage, TransApplicationLanguage, TransModelLanguage, \
    TransItemLanguage


@admin.register(TransApplicationLanguage)
class TransApplicationLanguageAdmin(admin.ModelAdmin):
    filter_horizontal = ('languages', )
    list_display = ('application', '_languages')
    form = TransApplicationLanguageAdminForm


@admin.register(TransModelLanguage)
class TransModelLanguageAdmin(admin.ModelAdmin):
    search_fields = ('model', )
    filter_horizontal = ('languages', )
    list_display = ('model', '_languages')
    list_filter = ('model', 'languages')
    form = TransModelLanguageAdminForm

    def save_model(self, request, obj, form, change):
        """
        Check if there are changes in the languages of a model and if so,
        delete or generate the translations tasks
        @todo add the process to a  queue

        :param request:
        :param obj:
        :param form:
        :param change:
        :return:
        """

        # gather the previous and the actual values
        try:
            old_langs_codes = [lang.code for lang in obj.languages.all()]
        except ValueError:
            old_langs_codes = []
        new_langs_codes = [lang.code for lang in form.cleaned_data['languages']]

        # check which langs are deleted
        to_remove = []
        for lang in old_langs_codes:
            if lang not in new_langs_codes:
                to_remove.append(lang)

        # check which langs are added
        to_add = []
        for lang in new_langs_codes:
            if lang not in old_langs_codes:
                to_add.append(lang)

        # save the model
        super().save_model(request, obj, form, change)

        # if there are changes, we've to generate/delete the tasks
        # for those languages that have have been added or deleted
        if to_remove or to_add:
            mc = obj.get_model_class()
            if to_remove:
                for item in mc.objects.all():
                    delete_translations_for_item_and_its_children.delay(mc, item.pk, to_remove)
                messages.success(
                    request,
                    _('Iniciado proceso de eliminación de tareas de traduccion para: {}'.format(
                        ', '.join(str(lang) for lang in to_remove)
                    ))
                )
            if to_add:
                for item in mc.objects.all():
                    create_translations_for_item_and_its_children.delay(mc, item.pk, to_add)
                messages.success(
                    request,
                    _('Iniciado proceso de generación de tareas de traducción para: {}'.format(
                        ', '.join(str(lang) for lang in to_add)
                    ))
                )


@admin.register(TransUser)
class TransUserAdmin(admin.ModelAdmin):
    filter_horizontal = ('languages', )
    list_display = ('user', '_languages', 'active')


@admin.register(TransLanguage)
class TransLanguageAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'main_language')
    list_display_links = ('code', 'name')


@admin.register(TransTask)
class TransTaskAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Detalle', {
            'fields': (('user', 'language'), ('object_class', 'object_pk'),
                       'object_name', 'object_field', 'object_field_label',
                       'object_field_value', 'object_field_value_translation', 'done')
        }),
        ('Internal', {
            'fields': ('date_creation', 'date_modification', 'notified', 'date_notified', 'content_type' )
        }),
    )

    readonly_fields = ('date_creation', 'date_modification', 'date_notified', 'notified')
    list_display = ('user', 'language', 'object_class', 'object_pk', 'object_field_label',
                    'date_creation', 'date_modification')
    list_filter = ('done', 'user', 'language', 'object_class')

    # def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
    #     field = super().formfield_for_foreignkey(db_field, request, **kwargs)
    #
    #     if db_field.name == 'content_type':
    #         apps = [item.model.split(' - ')[0] for item in TransModelLanguage.objects.all()]
    #         field.queryset = field.queryset.filter(app_label__in=apps).exclude(
    #             model__icontains='translation'
    #         ).order_by('app_label', 'model')
    #
    #     return field


@admin.register(TransItemLanguage)
class TransItemLanguageAdmin(admin.ModelAdmin):
    list_filter = ('content_type', 'object_id')
    list_display = ('id', 'content_type', 'object_id', 'content_object', '_languages')
    filter_horizontal = ('languages', )

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'content_type':
            kwargs['queryset'] = ContentType.objects.exclude(model__contains='translation').order_by('model')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
