============
TransManager
============

TransManager is a simple django app to deal with the translations tasks of the models content based on django-hvad.
It's not for static files.


Quick start
-----------

1. Add "transmanager" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'transmanager',
    ]

2. Include the transmanager URLconf in your project urls.py like this::

    url(r'^transmanager', include('transmanager.urls')),

3. Run `python manage.py migrate transmanager` to create the transmanager models.

4. Start de development server and visit: http://127.0.0.1:8000/admin/transmanager/
   then you can setup the languages and the translators users.

5.  Start updating your models content and you'll see the translation tasks appear.


