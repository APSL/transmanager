Installation
============

In order to install **TransManager** you need to do it via :code:`pip install transmanager`.

Then you've to append :code:`transmanager` to :code:`INSTALLED_APPS` in your settings.

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'transmanager'
    )


Execute the migrate command in order to create the models.

:code:`python manage.py migrate transmanager`


If you install **TransManager** in an app with already existing data, you can use the following
command in order to generate the translations tasks.

:code:`python manage.py generate_tasks`


