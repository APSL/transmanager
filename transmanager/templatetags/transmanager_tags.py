# -*- encoding: utf-8 -*-

from django.contrib.contenttypes.models import ContentType
from ..manager import Manager
from django import template
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from transmanager.models import TransLanguage
from transmanager.settings import TM_API_URL

register = template.Library()


@register.simple_tag(takes_context=True)
def show_list_translations(context, item):
    """
    Return the widget to select the translations we want
    to order or delete from the item it's being edited

    :param context:
    :param item:
    :return:
    """
    if not item:
        return

    manager = Manager()
    manager.set_master(item)

    ct_item = ContentType.objects.get_for_model(item)

    item_language_codes = manager.get_languages_from_item(ct_item, item)
    model_language_codes = manager.get_languages_from_model(ct_item.app_label, ct_item.model)

    item_languages = [{'lang': lang, 'from_model': lang.code in model_language_codes}
                      for lang in TransLanguage.objects.filter(code__in=item_language_codes).order_by('name')]

    more_languages = [{'lang': lang, 'from_model': lang.code in model_language_codes}
                      for lang in TransLanguage.objects.exclude(main_language=True).order_by('name')]

    return render_to_string('languages/translation_language_selector.html', {
        'item_languages': item_languages,
        'more_languages': more_languages,
        'api_url': TM_API_URL,
        'app_label': manager.app_label,
        'model': manager.model_label,
        'object_pk': item.pk
    })


@register.simple_tag()
def get_main_menu():
    """
    tag que devuelve las opciones del menú de la aplicación
    :return:
    """
    menu = [
        {'name': _("Tareas pendiente traducción"),
         'icon': 'fa fa-product-hunt',
         'url': 'transmanager-task-list'
         },
    ]

    return render_to_string('menu/main_menu.html', {'menu': menu})
