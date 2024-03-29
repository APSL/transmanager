# -*- encoding: utf-8 -*-

import uuid
import sys

from .settings import TM_DISABLED
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _
from parler.signals import pre_translation_save
from .signals import object_on_pre_save


class TransManagerConfig(AppConfig):
    name = 'transmanager'
    verbose_name = _('Gestor de traducciones')

    def ready(self):
        if 'test' in sys.argv:
            return
        if TM_DISABLED:
            return
        self.activate_pre_save_signal_for_models()

    @staticmethod
    def activate_pre_save_signal_for_models():
        from django.contrib.contenttypes.models import ContentType
        from parler.models import TranslatableModel
        try:
            # translatable models
            for it in ContentType.objects.all():
                try:
                    if issubclass(it.model_class(), TranslatableModel):
                        pre_translation_save.connect(object_on_pre_save, sender=it.model_class(), dispatch_uid=uuid.uuid4())
                except TypeError:
                    pass
        except Exception:
            pass
