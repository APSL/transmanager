# -*- encoding: utf-8 -*-

import logging

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from transmanager.signals import SignalBlocker
from django.utils.translation import gettext as _
from .utils import get_num_words

logger = logging.getLogger(__name__)


class TransLanguage(models.Model):
    code = models.CharField(max_length=2, verbose_name=_(u'Código'), help_text=_(u'Código ISO del idioma'))
    name = models.CharField(max_length=40, verbose_name=_(u'Nombre'))
    main_language = models.BooleanField(default=False, verbose_name=_(u'Idioma principal'),
                                        help_text=_(u'¿Es el idioma principal?'))

    class Meta:
        verbose_name = _(u'Idioma')
        verbose_name_plural = _(u'Idiomas')

    def __str__(self):
        return '{0}'.format(self.name)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """
        Overwrite of the save method in order that when setting the language
        as main we deactivate any other model selected as main before

        :param force_insert:
        :param force_update:
        :param using:
        :param update_fields:
        :return:
        """
        super().save(force_insert, force_update, using, update_fields)
        if self.main_language:
            TransLanguage.objects.exclude(pk=self.pk).update(main_language=False)


class TransUser(models.Model):
    user = models.OneToOneField(User, verbose_name=_(u'Usuario'), related_name='translator_user')
    languages = models.ManyToManyField(TransLanguage, verbose_name=_(u'Idiomas'))
    active = models.BooleanField(default=True, verbose_name=_(u'Activo'))

    class Meta:
        verbose_name = _(u'Traductor')
        verbose_name_plural = _(u'Traductores')

    def __str__(self):
        return '{0} - {1}'.format(self.user, _(u'Activo') if self.active else _(u'No activo'))

    # def __str__(self):
    #     return '{0} - {1} - {2}'.format(self.user,
    #                                     _(u'Activo') if self.active else _(u'No activo'),
    #                                     ', '.join([lang.name for lang in self.languages.all()]))

    def _languages(self):
        return ', '.join([lang.name for lang in self.languages.order_by('name')])
    _languages.short_description = _('Idiomas')


class TransTask(models.Model):

    # no editables per l'usuari
    user = models.ForeignKey(TransUser, verbose_name=_(u'Usuario'), related_name='tasks')
    language = models.ForeignKey(TransLanguage, verbose_name=_(u'Idioma'))
    object_class = models.CharField(verbose_name=_(u'Clase'), max_length=100, help_text=_(u'Clase del objeto'))
    object_pk = models.IntegerField(verbose_name=_(u'Clave'), help_text=_(u'Clave primária del objeto'))
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name=_(u'Fecha creación'))
    date_modification = models.DateTimeField(auto_now=True, verbose_name=_(u'Fecha modificación'))
    notified = models.BooleanField(default=False, verbose_name=_(u'Notificada'),
                                   help_text=_(u'Si la tarea ya ha sido notificada o no al usuario'))
    date_notified = models.DateTimeField(blank=True, null=True, verbose_name=_(u'Fecha notificacion'))
    content_type = models.ForeignKey(ContentType, verbose_name=_('Modelo'), blank=True, null=True)

    # editables
    object_name = models.CharField(verbose_name=_(u'Nombre objeto'), max_length=200)
    object_field = models.CharField(verbose_name=_(u'Nombre campo'), max_length=200,
                                    help_text=_(u'Nombre del atributo en el modelo'))
    object_field_label = models.CharField(verbose_name=_(u'Descripción campo'), max_length=200,
                                          help_text=_(u'Etiqueta del campo'))
    object_field_value = models.TextField(verbose_name=_(u'Valor'),
                                          help_text=_(u'Valor del campo en el idioma principal'))

    object_field_value_translation = models.TextField(verbose_name=_(u'Valor traducido'), blank=True, null=True,
                                                      help_text=_(u'Valor traducido del campo en el idioma principal'))

    number_of_words = models.IntegerField(verbose_name=_('Número palabras'), default=0,
                                          help_text=_('Número de palabras a traducir en el idioma original'))

    done = models.BooleanField(default=False, verbose_name=_(u'Hecho'))

    class Meta:
        verbose_name = _(u'Tarea')
        verbose_name_plural = _(u'Tareas')
        # unique_together = ('object_class', 'object_pk', 'object_field')
        ordering = ['-id']

    def __str__(self):
        return '{0} - {1} - {2} - {3} - {4}'.format(self.user, self.language,
                                                    self.object_name, self.object_field, self.object_field_value)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.number_of_words = get_num_words(self.object_field_value)
        super().save(force_insert, force_update, using, update_fields)

        # get the model to update
        if self.object_field_value_translation and self.object_field_value_translation != '':

            app_label, model = self.get_natural_key()
            ct = ContentType.objects.get_by_natural_key(app_label, model)

            try:
                item = ct.model_class().objects.language(self.language.code).get(pk=self.object_pk)
            except ObjectDoesNotExist:
                # we get the shared model (untranslated) and then create the translation
                try:
                    item = ct.model_class().objects.untranslated().get(pk=self.object_pk)
                except ObjectDoesNotExist:
                    # if we not found the shared model (untranslated) we do nothing
                    return
                item.translate(self.language.code)
            with SignalBlocker(pre_save):
                setattr(item, self.object_field, self.object_field_value_translation)
                item.save()

    def get_natural_key(self):
        return self.object_name.split('-')[0].strip(), self.object_class.lower().strip()

    def get_model_class(self):
        app_label, model = self.get_natural_key()
        try:
            ct = ContentType.objects.get_by_natural_key(app_label, model)
        except ContentType.DoesNotExist:
            return
        return ct.model_class()


class TransApplicationLanguage(models.Model):

    application = models.CharField(max_length=100, verbose_name=_('Aplicación'), unique=True)
    languages = models.ManyToManyField(TransLanguage, verbose_name=_('Idiomas'),
                                       help_text=_('Idiomas por defecto de la aplicación'))

    class Meta:
        verbose_name = _('Idiomas por aplicación')
        verbose_name_plural = _('Idiomas por aplicaciones')

    def __str__(self):
        return self.application

    def _languages(self):
        return ', '.join([lang.name for lang in self.languages.order_by('name')])
    _languages.short_description = _('Idiomas')


class TransModelLanguage(models.Model):

    model = models.CharField(max_length=100, verbose_name=_('Modelo'), unique=True)
    languages = models.ManyToManyField(TransLanguage, verbose_name=_('Idiomas'),
                                       help_text=_('Idiomas por defecto del modelo'))

    class Meta:
        verbose_name = _('Idiomas por modelo')
        verbose_name_plural = _('Idiomas por modelos')

    def __str__(self):
        return self.model

    def _languages(self):
        return ', '.join([lang.name for lang in self.languages.order_by('name')])
    _languages.short_description = _('Idiomas')

    def get_model_class(self):
        app_label, model = self.model.split(' - ')
        try:
            ct_model = ContentType.objects.get_by_natural_key(app_label, model)
        except ContentType.DoesNotExist:
            return
        return ct_model.model_class()


class TransItemLanguage(models.Model):

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name=_('Modelo'))
    object_id = models.PositiveIntegerField(verbose_name=_('Identificador'))
    content_object = GenericForeignKey('content_type', 'object_id')
    languages = models.ManyToManyField(TransLanguage, verbose_name=_('Idiomas'),
                                       help_text=_('Idiomas por defecto del item'))

    class Meta:
        verbose_name = _('Idiomas por item')
        verbose_name_plural = _('Idiomas por item')

    def __str__(self):
        return '{}'.format(self.content_object)

    def _languages(self):
        return ', '.join([lang.name for lang in self.languages.order_by('name')])
    _languages.short_description = _('Idiomas')
