# -*- encoding: utf-8 -*-

import logging
from transmanager.tasks.tasks import create_translations_for_item_and_its_children, \
    delete_translations_for_item_and_its_children

logger = logging.getLogger(__name__)


class TranslationTasksMixin(object):
    """
    Mixin that allows to create/delete the translations tasks when the instance of the model is enabled/disabled
    """

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):

        create = False
        delete = False

        # get the previous instance
        if self.pk:
            prev = self.__class__.objects.get(pk=self.pk)
        else:
            prev = None

        # decide what to do
        if not self.pk and self.enabled:
            # new instance
            create = True
        elif self.pk and self.enabled and prev and not prev.enabled:
            # from disabled to enabled
            create = True
        elif self.pk and not self.enabled and prev and prev.enabled:
            # from enabled to disabled
            delete = True

        super().save(force_insert, force_update, using, update_fields)

        if create:
            logger.info('X' * 20)
            logger.info('CREATING FOR ITEM AND CHILDREN')
            create_translations_for_item_and_its_children.delay(self.__class__, self.pk)
            logger.info('END FOR ITEM AND CHILDREN\n\n')
        elif delete:
            logger.info('X' * 20)
            logger.info('DELETING FOR ITEM AND CHILDREN')
            delete_translations_for_item_and_its_children.delay(self.__class__, self.pk)
            logger.info('END FOR ITEM AND CHILDREN\n\n')
