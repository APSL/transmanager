# -*- encoding: utf-8 -*-

"""
Common serializers to be used by the own serializers from each API module
"""
from transmanager.models import TransTask, TransLanguage, TransUser
from .manager import Manager
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from rest_framework.fields import ListField
from rest_framework import serializers
from .tasks.tasks import delete_translations_for_item_and_its_children, create_translations_for_item_and_its_children


class TaskBulksSerializer(serializers.Serializer):
    app_label = serializers.CharField(required=True)
    model = serializers.CharField(required=True)
    languages = ListField(required=True)
    ids = ListField(required=True)

    class Meta:
        fields = ('app_label', 'model', 'languages', 'ids')

    def validate(self, attrs):
        try:
            self.model_class = None
            self.app_label = attrs['app_label'].strip()
            self.model = attrs['model'].strip()
            self.languages = attrs['languages']
            self.ids = attrs['ids']
            if not self.languages:
                raise serializers.ValidationError(detail=_('No se han especificado códigos de idioma'))
            if not self.ids:
                raise serializers.ValidationError(detail=_('No se han especificado códigos de item'))
            ct = ContentType.objects.get_by_natural_key(self.app_label.lower(), self.model.lower())
            if not ct:
                raise serializers.ValidationError(detail=_('El Content Type no existe'))
            self.model_class = ct.model_class()
            return attrs
        except Exception as e:
            raise serializers.ValidationError(detail=str(e))

    def save(self, **kwargs):
        """
        Method that creates the translations tasks for every selected instance

        :param kwargs:
        :return:
        """
        try:
            # result_ids = []
            manager = Manager()
            for item in self.model_class.objects.language(manager.get_main_language()).filter(pk__in=self.ids).all():
                create_translations_for_item_and_its_children.delay(self.model_class, item.pk, self.languages,
                                                                    update_item_languages=True)
            # return TransTaskSerializer(TransTask.objects.filter(pk__in=result_ids), many=True).data
            return {'status': 'ok'}
        except Exception as e:
            raise serializers.ValidationError(detail=str(e))

    def delete(self, **kwargs):
        """
        Method that deletes the translations tasks for every selected instance

        :param kwargs:
        :return:
        """
        try:
            manager = Manager()
            for item in self.model_class.objects.language(manager.get_main_language()).filter(pk__in=self.ids).all():
                delete_translations_for_item_and_its_children.delay(self.model_class, item.pk, self.languages,
                                                                    update_item_languages=True)
            return
        except Exception as e:
            raise serializers.ValidationError(detail=str(e))


class TransLanguageSerializer(serializers.ModelSerializer):

    class Meta:
        model = TransLanguage
        fields = ('code', 'name')


class TransUserSerializer(serializers.ModelSerializer):

    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.CharField(source='user.email')
    languages = serializers.SerializerMethodField()

    @staticmethod
    def get_languages(obj):
        return ', '.join([lang.code for lang in obj.languages.all()])

    class Meta:
        model = TransUser
        fields = ('first_name', 'last_name', 'email', 'languages')


class TransTaskSerializer(serializers.ModelSerializer):

    user = TransUserSerializer()
    language = TransLanguageSerializer()

    class Meta:
        model = TransTask
        fields = (
            'user', 'language', 'object_class', 'object_pk', 'date_creation', 'date_modification', 'notified',
            'date_notified', 'object_name', 'object_field', 'object_field_label', 'object_field_value',
            'object_field_value_translation', 'done'
        )
