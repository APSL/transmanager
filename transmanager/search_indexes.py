# -*- encoding: utf-8 -*-

import datetime
from haystack import indexes
from .models import TransTask


class TransTaskIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    object_field_value_translation = indexes.CharField(model_attr='object_field_value_translation', null=True)
    language = indexes.CharField(model_attr='language')
    user = indexes.CharField(model_attr='user')

    def get_model(self):
        return TransTask

    def index_queryset(self, using=None):
        """
        Used when the entire index for model is updated.
        """
        return self.get_model().objects.filter(date_creation__lte=datetime.datetime.now())
