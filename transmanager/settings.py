# -*- encoding: utf-8 -*-
"""
Settings for TransManager app
"""

from django.conf import settings

TM_API_URL = '/transmanager/api/task/'
TM_DEFAULT_LANGUAGE_CODE = getattr(settings, 'TRANSMANAGER_DEFAULT_LANGUAGE_CODE', 'es')
TM_DEFAULT_ENABLED_ATTRIBUTE_NAME = getattr(settings, 'TRANSMANAGER_DEFAULT_ENABLED_ATTRIBUTE_NAME', 'enabled')
TM_BRAND_LOGO_URL = getattr(settings, 'TM_BRAND_LOGO_URL', 'transmanager/img/logo.png')
TM_ORIGINAL_VALUE_CHARS_NUMBER = getattr(settings, 'TM_ORIGINAL_VALUE_CHARS_NUMBER', 100)
TM_HAYSTACK_DISABLED = getattr(settings, 'TM_HAYSTACK_DISABLED', False)
TM_HAYSTACK_SUGGESTIONS_MAX_NUMBER = getattr(settings, 'TM_HAYSTACK_SUGGESTIONS_MAX_NUMBER', 20)
