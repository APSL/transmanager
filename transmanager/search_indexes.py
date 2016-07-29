# -*- encoding: utf-8 -*-

import datetime
from haystack import indexes
from .models import TransTask


class TransTaskIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    has_value = indexes.CharField(model_attr='has_value')
    language = indexes.CharField(model_attr='language')
    user = indexes.CharField(model_attr='user')

    def get_model(self):
        return TransTask

    def index_queryset(self, using=None):
        """
        Used when the entire index for model is updated.
        """
        return self.get_model().objects.filter(date_creation__lte=datetime.datetime.now())
