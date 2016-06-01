# -*- encoding: utf-8 -*-
"""
Settings for TransManager app
"""

from django.conf import settings

TM_LANGUAGES_FIELD_NAME = getattr(settings, 'TRANSMANAGER_LANGUAGES_FIELD_NAME', 'languages')
TM_DEFAULT_LANGUAGE_CODE = getattr(settings, 'TRANSMANAGER_DEFAULT_LANGUAGE_CODE', 'es')
TM_DEFAULT_ENABLED_ATTRIBUTE_NAME = getattr(settings, 'TRANSMANAGER_DEFAULT_ENABLED_ATTRIBUTE_NAME', 'enabled')
TM_API_URL = '/transmanager/api/task/'
