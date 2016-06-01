# -*- encoding: utf-8 -*-

import logging
from datetime import datetime
from threading import Lock

from django.contrib.admin.utils import NestedObjects
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from hvad.models import BaseTranslationModel, TranslatableModel
from hvad.utils import get_translation

from .models import TransTask, TransUser, TransLanguage, TransModelLanguage, TransApplicationLanguage, TransItemLanguage
from .settings import TM_DEFAULT_LANGUAGE_CODE, TM_DEFAULT_ENABLED_ATTRIBUTE_NAME

logger = logging.getLogger(__name__)


class Manager(object):
    """
    Class that handle the creation of translations task checking the instance in the main language of a model.

    For new instances, create a task for every translatable field
    that has a value in the main language

    For existing instances, create a task for every translatable field
    that has been modified in the main language and has a value

    """
    def __init__(self):
        self.instance_class = None
        self.master = None
        self.master_class = None
        self.app_label = None
        self.instance = None
        self.created = False
        self.sender = None
        self.translators = self.get_users_indexed_by_lang()
        self.main_language = self.get_main_language()
        self.lock = Lock()
        self.ct_master = None
        self.app_label = None
        self.model_label = None
        # check if there is already a value for the destinatation lang
        # when we are in bulk mode, when we are in signal mode
        # we update the destination task if it exists
        self.bulk_mode = False

    def set_sender(self, sender):
        self.sender = sender

    def set_instance(self, instance):
        self.instance = instance
        self.instance_class = instance._meta.model.__name__
        self.set_master(instance.master)

    def set_master(self, master):
        self.master = master
        try:
            self.ct_master = ContentType.objects.get_for_model(master)
            self.master_class = self.ct_master.model_class()
            self.app_label = self.ct_master.app_label
            self.model_label = self.ct_master.model
        except ContentType.DoesNotExist:
            raise Exception('TransManager - unable to find ContentType for master')

    def start(self, sender, instance=None, **kwargs):

        self.set_instance(instance)
        self.sender = sender
        self.created = kwargs.get('created', False)

        # check if the object is translatable
        if not self.check_object():
            return

        self.log('------------ INIT ------------')

        if self.is_parent(self.master):
            # parent model
            self.log('MASTER ' * 5)
            action = 'translate' if self.is_instance_enabled(self.master) else 'delete'
        elif self.is_child(self.master):
            self.log('CHILD ' * 5)
            # child model
            action = 'translate' if self.is_parent_enabled(self.master) else 'delete'
        else:
            self.log('NORMAL ' * 5)
            # normal model
            action = 'translate'

        # if self.is_instance_enabled(self.instance.master):
        if action == 'translate':
            # instance active, then we create the translations
            # MAIN LANGUAGE?
            if self.instance.language_code == self.get_main_language():
                # YES, then we create/update the tasks for alternative languages
                self.log('------------ INIT CREATE------------')
                self.create_translation_tasks(self.instance)
                self.log('------------ END CREATE------------')
            elif not self.created:
                # NO, then we try to update the task as done if the existing alternative language record has value
                self.update_translations_tasks(self.instance)
        elif action == 'delete':
            # if the instance is not active we delete de translations it couild have
            self.delete_translations_for_item_and_its_children(self.master)

        self.log('------------ END ------------')

    def create_translation_tasks(self, instance):
        """
        Creates the translations tasks from the instance and its translatable children

        :param instance:
        :return:
        """

        langs = self.get_languages()

        result = []
        # get the previous and actual values
        # in case it's and "add" operation previous values will be empty
        previous_values, actual_values = self.get_previous_and_current_values(instance)

        # extract the differences
        differences = self.extract_diferences(previous_values, actual_values)
        self.log('\nprev: {}\nactu:{}\ndiff:{}'.format(previous_values, actual_values, differences))
        if len(differences) > 0:
            # there are differences in the main model, so we create the tasks for it
            result += self.create_from_item(langs, instance.master, differences, trans_instance=self.instance)
        else:
            # no differences so we do nothing to the main model
            self.log('No differences we do nothing CREATE {}:{}'.format(self.master_class, instance.language_code))
        return result

    def update_translations_tasks(self, instance):
        # check if the instance language is in the languages configured for the model?
        lang = instance.language_code
        if not self.is_desired_language(lang):
            self.log('avoiding: {} '.format(lang))
            return

        # get the previous and actual values
        # in this case will be always update value operation and previous values will be NOT empty
        previous_values, actual_values = self.get_previous_and_current_values(instance)

        # extract the differences
        differences = self.extract_diferences(previous_values, actual_values)
        if len(differences) == 0:
            self.log('No differences WHILE UPDATING in {}, so we do nothing'.format(lang))
            return

        self.update_task(differences)

    def update_task(self, differences):
        """
        Updates a task as done if we have a new value for this alternative language

        :param differences:
        :return:
        """

        self.log('differences UPDATING: {}'.format(differences))

        object_name = '{} - {}'.format(self.app_label, self.instance.master._meta.verbose_name)
        lang = self.instance.language_code
        object_pk = self.instance.master.pk

        for field in differences:
            value = getattr(self.instance, field)
            if value is None or value == '':
                continue
            try:
                TransTask.objects.filter(
                    language__code=lang, object_field=field, object_name=object_name, object_pk=object_pk
                ).update(done=True, date_modification=datetime.now(), object_field_value_translation=value)
                self.log('MARKED TASK AS DONE')
            except TransTask.DoesNotExist:
                self.log('error MARKING TASK AS DONE: {} - {} - {} - {}'.format(lang, field, object_name, object_pk))

    def extract_diferences(self, previous_values, current_values):
        result = set()
        for key, act_value in current_values.items():
            if key not in previous_values:
                result.add(key)
            pre_value = previous_values.get(key)
            # check if the previous and current value are equal and the current value exists
            if act_value != pre_value:
                result.add(key)

        if len(result) > 0:
            self.log('DIFFERENCES: {}'.format(result))
            self.log('previous values: {}'.format(previous_values))
            self.log('actual values: {}'.format(current_values))

        return result

    def check_object(self):
        """
        Checks whether or not to process an object
        We only process a translation tuple in the original language
        in order to detect if it has suffered changes or not
        :return:
        """
        # if not isinstance(self.instance, TranslatableModel):
        if not issubclass(self.sender, BaseTranslationModel):
            return False
        return True

    def get_previous_and_current_values(self, instance):
        """
        Obtain the previous and actual values and compares them
        in order to detect which fields has changed

        :param instance:
        :param translation:
        :return:
        """
        translated_field_names = self._get_translated_field_names(instance.master)
        if instance.pk:
            try:
                previous_obj = instance._meta.model.objects.get(pk=instance.pk)
                previous_values = self.get_obj_values(previous_obj, translated_field_names)
            except ObjectDoesNotExist:
                previous_values = {}
        else:
            previous_values = {}
        current_values = self.get_obj_values(instance, translated_field_names)
        return previous_values, current_values

    @staticmethod
    def get_obj_values(obj, translated_field_names):
        """
        get the translated field values from translatable fields of an object

        :param obj:
        :param translated_field_names:
        :return:
        """
        # set of translated fields to list
        fields = list(translated_field_names)
        values = {field: getattr(obj, field) for field in fields}
        return values

    @staticmethod
    def _get_translated_field_names(model_instance):
        """
        Get the instance translatable fields

        :return:
        """
        hvad_internal_fields = ['id', 'language_code', 'master', 'master_id', 'master_id']
        translated_field_names = set(model_instance._translated_field_names) - set(hvad_internal_fields)
        return translated_field_names

    def get_languages(self, include_main=False):
        """
        Get all the languages except the main.

        Try to get in order:
            1.- item languages
            2.- model languages
            3.- application model languages
            # 4.- default languages

        :param master:
        :param include_main:
        :return:
        """

        if not self.master:
            raise Exception('TransManager - No master set')

        item_languages = self.get_languages_from_item(self.ct_master, self.master)

        languages = self.get_languages_from_model(self.ct_master.app_label, self.ct_master.model)
        if not languages:
            languages = self.get_languages_from_application(self.ct_master.app_label)
            # if not languages:
            #     languages = self.get_languages_default()

        if not include_main:
            main_language = self.get_main_language()
            if main_language in languages:
                languages.remove(main_language)

        return list(set(item_languages + languages))

    @staticmethod
    def get_users_indexed_by_lang():
        """
        Return all the translator users indexed by lang
        :return:
        """
        result = {}
        users = TransUser.objects.filter(active=True).select_related('user')
        for user in users:
            for lang in user.languages.all():
                if lang.code not in result:
                    result[lang.code] = set()
                result[lang.code].add(user)
        return result

    @staticmethod
    def get_languages_from_item(ct_item, item):
        """
        Get the languages configured for the current item
        :param ct_item:
        :param item:
        :return:
        """
        try:
            item_lan = TransItemLanguage.objects.filter(content_type__pk=ct_item.id, object_id=item.id).get()
            languages = [lang.code for lang in item_lan.languages.all()]
            return languages
        except TransItemLanguage.DoesNotExist:
            return []

    @staticmethod
    def get_languages_from_model(app_label, model_label):
        """
        Get the languages configured for the current model

        :param model_label:
        :param app_label:
        :return:
        """
        try:
            mod_lan = TransModelLanguage.objects.filter(model='{} - {}'.format(app_label, model_label)).get()
            languages = [lang.code for lang in mod_lan.languages.all()]
            return languages
        except TransModelLanguage.DoesNotExist:
            return []

    @staticmethod
    def get_languages_from_application(app_label):
        """
        Get the languages configured for the current application

        :param app_label:
        :return:
        """
        try:
            mod_lan = TransApplicationLanguage.objects.filter(application=app_label).get()
            languages = [lang.code for lang in mod_lan.languages.all()]
            return languages
        except TransApplicationLanguage.DoesNotExist:
            return []

    @staticmethod
    def get_languages_default():
        """
        Get default languages. used in case the model and the app does not have languages configured

        :return:
        """
        languages = [it.code for it in TransLanguage.objects.all()]
        return languages

    @staticmethod
    def get_main_language():
        """
        returns the main language
        :return:
        """
        try:
            main_language = TransLanguage.objects.filter(main_language=True).get()
            return main_language.code
        except TransLanguage.DoesNotExist:
            return TM_DEFAULT_LANGUAGE_CODE

    def log(self, msg):
        """
        Log a message information adding the master_class and instance_class if available

        :param msg:
        :return:
        """
        if self.master_class and self.instance_class:
            logger.info('{0} - {1} - {2} - {3} - lang: {4} msg: {5}'.format(
                self.ct_master.app_label, self.ct_master.model,
                self.instance_class, self.instance.language_code, self.instance.pk, msg)
            )
        elif self.instance_class:
            logger.info('{} - {}: {}'.format(self.instance_class, self.instance.pk, msg))
        else:
            logger.info('{}'.format(msg))

    def is_desired_language(self, lang):
        """
        Check is a language is in the languages of the (model, application, default)

        :param lang:
        :return:
        """
        return lang in self.get_languages()

    def create_from_item(self, languages, item, fields, trans_instance=None):
        """
        Creates tasks from a model instance "item" (master)
        Used in the api call

        :param languages:
        :param item:
        :param fields:
        :param trans_instance: determines if we are in bulk mode or not.
        If it has a value we're processing by the signal trigger,
        if not we're processing either by the api or the mixin
        :return:
        """
        if not isinstance(item, TranslatableModel):
            return

        self.log('gonna parse fields: {}'.format(fields))

        with self.lock:
            result = []

            if trans_instance:
                # get the values from the instance that is being saved, values not saved yet
                trans = trans_instance
            else:
                # get the values from the db instance
                trans = self.get_translation_from_instance(item, self.main_language)

            if not trans:
                return

            for field in fields:

                self.log('parsing field: {}'.format(field))

                # for every field
                object_field_label = self.get_field_label(trans, field)
                object_field_value = getattr(trans, field)
                # if object_field_value is None or object_field_value == '':
                #     object_field_value = getattr(self.instance, field, '')

                self.log('object_field_value for {} - .{}.'.format(object_field_label, object_field_value))

                if object_field_value == '' or object_field_value is None:
                    continue
                for lang in languages:
                    # for every language
                    self.log('parsing lang: {}'.format(lang))

                    language = TransLanguage.objects.filter(code=lang).get()
                    users = self.translators.get(lang, [])

                    self.log('gonna parse users')

                    for user in users:
                        # for every user we create a task

                        # check if there is already a value for the destinatation lang
                        # when we are in bulk mode, when we are in signal mode
                        # we update the destination task if it exists
                        if self.bulk_mode and self.exists_destination_lang_value(item, field, lang):
                            continue

                        ob_class_name = item.__class__.__name__

                        self.log('creating or updating object_class: {} | object_pk:{} | object_field: {}'.format(
                            ob_class_name,
                            item.pk,
                            field
                        ))

                        app_label = item._meta.app_label
                        model = ob_class_name.lower()
                        ct = ContentType.objects.get_by_natural_key(app_label, model)

                        try:
                            task, created = TransTask.objects.get_or_create(
                                content_type=ct,
                                object_class=ob_class_name,
                                object_pk=item.pk,
                                object_field=field,
                                language=language,
                                user=user,
                                defaults={
                                    'object_name': '{} - {}'.format(app_label, item._meta.verbose_name),
                                    'object_field_label': object_field_label,
                                    'object_field_value': object_field_value,
                                    'done': False
                                }
                            )
                            if not created:
                                self.log('updating')
                                task.date_modification = datetime.now()
                                task.object_field_value = object_field_value
                                task.done = False
                                task.save()
                            result.append(task)
                        except TransTask.MultipleObjectsReturned:
                            # theorically it should not occur but if so delete the repeated tasks
                            TransTask.objects.filter(object_class=ob_class_name, object_pk=item.pk, object_field=field,
                                                     language=language, user=user)[1:].delete()

        # we return every task (created or modified)
        return result

    def get_field_label(self, trans, field):
        """
        Get the field label from the _meta api of the model

        :param trans:
        :param field:
        :return:
        """
        try:
            # get from the instance
            object_field_label = trans._meta.get_field_by_name(field)[0].verbose_name
        except Exception:
            try:
                # get from the class
                object_field_label = self.sender._meta.get_field_by_name(field)[0].verbose_name
            except Exception:
                # in the worst case we set the field name as field label
                object_field_label = field
        return object_field_label

    def get_translatable_children(self, obj):
        """
        Obtain all the translatable children from "obj"

        :param obj:
        :return:
        """
        collector = NestedObjects(using='default')
        collector.collect([obj])
        object_list = collector.nested()
        items = self.get_elements(object_list)
        # avoid first object because it's the main object
        return items[1:]

    def get_elements(self, object_list):
        """
        Recursive method to iterate the tree of children in order to flatten it

        :param object_list:
        :return:
        """
        result = []
        for item in object_list:
            if isinstance(item, list):
                result += self.get_elements(item)
            elif isinstance(item, TranslatableModel):
                result.append(item)
        return result

    def update_model_languages(self, model_class, languages):
        """
        Update the TransModelLanguages model with the selected languages

        :param model_class:
        :param languages:
        :return:
        """
        # get the langs we have to add to the TransModelLanguage
        qs = TransLanguage.objects.filter(code__in=languages)
        new_langs = [lang for lang in qs]
        if not new_langs:
            return
        mod_lan, created = TransModelLanguage.objects.get_or_create(
            model='{} - {}'.format(model_class._meta.app_label, model_class._meta.model.__name__.lower()),
        )

        exist_langs_codes = [lang.code for lang in mod_lan.languages.all()]
        for lang in new_langs:
            if lang.code not in exist_langs_codes:
                try:
                    mod_lan.languages.add(lang)
                except IntegrityError:
                    pass

    def add_item_languages(self, item, languages):
        """
        Update the TransItemLanguage model with the selected languages

        :param item:
        :param languages:
        :return:
        """
        # get the langs we have to add to the TransModelLanguage
        qs = TransLanguage.objects.filter(code__in=languages)
        new_langs = [lang for lang in qs]
        if not new_langs:
            return

        ct_item = ContentType.objects.get_for_model(item)
        item_lan, created = TransItemLanguage.objects.get_or_create(content_type_id=ct_item.id, object_id=item.id)
        item_lan.languages.add(*new_langs)

    def remove_item_languages(self, item, languages):
        """
        delete the selected languages from the TransItemLanguage model

        :param item:
        :param languages:
        :return:
        """
        # get the langs we have to add to the TransModelLanguage
        qs = TransLanguage.objects.filter(code__in=languages)
        remove_langs = [lang for lang in qs]
        if not remove_langs:
            return

        ct_item = ContentType.objects.get_for_model(item)
        item_lan, created = TransItemLanguage.objects.get_or_create(content_type_id=ct_item.id, object_id=item.id)
        for lang in remove_langs:
            item_lan.languages.remove(lang)
        if item_lan.languages.count() == 0:
            item_lan.delete()

    @staticmethod
    def get_translation_from_instance(instance, lang):
        """
        Get the translation from the instance in a specific language, hits the db

        :param instance:
        :param lang:
        :return:
        """
        try:
            translation = get_translation(instance, lang)
        except (AttributeError, ObjectDoesNotExist):
            translation = None
        return translation

    def create_translations_for_item_and_its_children(self, item, languages=None):
        """
        Creates the translations from an item and defined languages and return the id's of the created tasks

        :param item: (master)
        :param languages:
        :return:
        """

        if not self.master:
            self.set_master(item)

        if not languages:
            languages = self.get_languages()

        result_ids = []

        # first process main object
        fields = self._get_translated_field_names(item)
        tasks = self.create_from_item(languages, item, fields)
        if tasks:
            result_ids += [task.pk for task in tasks]

        # then process child objects from main
        children = self.get_translatable_children(item)
        for child in children:
            fields = self._get_translated_field_names(child)
            tasks = self.create_from_item(languages, child, fields)
            if tasks:
                result_ids += [task.pk for task in tasks]

        return result_ids

    def delete_translations_for_item_and_its_children(self, item, languages=None):
        """
        deletes the translations task of an item and its children
        used when a model is not enabled anymore
        :param item:
        :param languages:
        :return:
        """

        self.log('--- Deleting translations ---')

        if not self.master:
            self.set_master(item)

        object_name = '{} - {}'.format(item._meta.app_label.lower(), item._meta.verbose_name)
        object_class = item.__class__.__name__
        object_pk = item.pk

        filter_by = {
            'object_class': object_class,
            'object_name': object_name,
            'object_pk': object_pk,
            'done': False
        }
        if languages:
            filter_by.update({'language__code__in': languages})
        TransTask.objects.filter(**filter_by).delete()

        # then process child objects from main
        children = self.get_translatable_children(item)
        for child in children:
            self.delete_translations_for_item_and_its_children(child, languages)

    @staticmethod
    def is_instance_enabled(master):
        """
        Detect if an translatable instance is enabled
        :param master: the instance of the master model
        :return: boolean
        """
        if hasattr(master, TM_DEFAULT_ENABLED_ATTRIBUTE_NAME):
            return getattr(master, TM_DEFAULT_ENABLED_ATTRIBUTE_NAME)

    def is_parent_enabled(self, master):
        """
        Detect if a parent of an instance is enabled or not
        :param master: the instance of the master model
        :return: boolean
        """
        parent = master.get_parent()
        return self.is_instance_enabled(parent)

    @staticmethod
    def is_parent(master):
        return hasattr(master, TM_DEFAULT_ENABLED_ATTRIBUTE_NAME)

    @staticmethod
    def is_child(master):
        return hasattr(master, 'get_parent')

    @staticmethod
    def exists_destination_lang_value(item, field, lang):
        try:
            dest_trans = get_translation(item, lang)
            dest_object_field_value = getattr(dest_trans, field)
            if dest_object_field_value and dest_object_field_value.strip() != '':
                return True
        except (AttributeError, ObjectDoesNotExist):
            pass
        return False
