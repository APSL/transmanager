Settings
========

TransManager provides setting variables in order to customize your installation.


TM_DEFAULT_LANGUAGE_CODE
------------------------
The default language code in **ISO 639-1** format. Default ``'es'``.


.. _enabled:

TM_DEFAULT_ENABLED_ATTRIBUTE_NAME
---------------------------------
The name of the attribute that we have to watch in order to know if the record of the main model is enabled or not.
Watching the state of this field we order to generate or delete the translations of the main model record.
Default ``'enabled'``. See the :ref:`enabling_disabling` section.


TM_API_URL
----------
Url of the API of **TransManager**. Default ``'/transmanager/api/task/'``.


TM_BRAND_LOGO_URL
-----------------
Url of logo with which you can "brand" the list and edit tasks pages.
Default ``'transmanager/img/logo.png'``.


TM_ORIGINAL_VALUE_CHARS_NUMBER
------------------------------
Number of chars that we want to show from the value to translate in the translation task list. Default ``100``.



