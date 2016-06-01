# -*- encoding: utf-8 -*-

import django_rq
from rq.decorators import job
from transmanager.manager import Manager


@job('default', connection=django_rq.get_connection('default'))
def create_translations_for_item_and_its_children(model_class, item_id, languages=None, update_item_languages=False):
    do_action('create', model_class, item_id, languages, update_item_languages)


@job('default', connection=django_rq.get_connection('default'))
def delete_translations_for_item_and_its_children(model_class, item_id, languages=None, update_item_languages=False):
    do_action('delete', model_class, item_id, languages, update_item_languages)


def do_action(action, model_class, item_id, languages=None, update_item_languages=False):
    manager = Manager()
    manager.bulk_mode = True
    main_lang_code = manager.get_main_language()

    if languages and main_lang_code in languages:
        languages.remove(main_lang_code)

    try:
        item = model_class.objects.language(main_lang_code).get(pk=item_id)
    except model_class.DoesNotExist:
        return

    if action == 'create':
        manager.create_translations_for_item_and_its_children(item, languages)
        if update_item_languages:
            manager.add_item_languages(item, languages)
    elif action == 'delete':
        manager.delete_translations_for_item_and_its_children(item, languages)
        if update_item_languages:
            manager.remove_item_languages(item, languages)
