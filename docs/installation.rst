Installation
============

In order to install **TransManager** you need to do it via :code:`pip install transmanager`.

Then you've to append :code:`transmanager` and :code:`django_tables2` to :code:`INSTALLED_APPS` in your settings.

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'transmanager',
        'django_filters',
        'django_tables2',
        'haystack',
    )


Execute the migrate command in order to create the models.

:code:`python manage.py migrate transmanager`


If you install **TransManager** in an app with already existing data, you can use the following
command in order to generate the translations tasks.

:code:`python manage.py generate_tasks`


As **Transmanager** comes with a translations suggestion system enable by default, we have to generate
the index of the suggestions, which relies on a haystack search index. First we need to add the HAYSTACK_CONNECTIONS
to the main app settings:

.. code-block:: python

    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
            'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
        },
    }
    HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

It's recommended to activate the realtime signal processos in order to have the search index updated.
You can also cron the command :code:`python manage.py update_index`.
Take a look to the Django-haystack documentation_ for further information.

.. _documentation: http://django-haystack.readthedocs.io/en/latest/tutorial.html


