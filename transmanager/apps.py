# -*- encoding: utf-8 -*-

import uuid
import sys

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import pre_save
from hvad.models import BaseTranslationModel
from .signals import object_on_pre_save


class TransManagerConfig(AppConfig):
    name = 'transmanager'
    verbose_name = _('Gestor de traducciones')

    def ready(self):
        if 'test' in sys.argv:
            return
        self.activate_pre_save_signal_for_models()

    @staticmethod
    def activate_pre_save_signal_for_models():
        try:
            # translatable models
            for it in ContentType.objects.all():
                try:
                    if issubclass(it.model_class(), BaseTranslationModel):
                        pre_save.connect(object_on_pre_save, sender=it.model_class(), dispatch_uid=uuid.uuid4())
                except TypeError:
                    pass
        except Exception:
            pass
