# -*- encoding: utf-8 -*-


from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm
from django import forms
from transmanager.utils import get_model_choices, get_application_choices
from .models import TransTask, TransModelLanguage, TransApplicationLanguage


class TransApplicationLanguageAdminForm(ModelForm):

    class Meta:
        model = TransApplicationLanguage
        fields = ('application', 'languages')

    def __init__(self, *args, **kwargs):
        self.base_fields['application'].widget = forms.Select(choices=get_application_choices())
        super().__init__(*args, **kwargs)


class TransModelLanguageAdminForm(ModelForm):

    class Meta:
        model = TransModelLanguage
        fields = ('model', 'languages')

    def __init__(self, *args, **kwargs):
        self.base_fields['model'].widget = forms.Select(choices=get_model_choices())
        super().__init__(*args, **kwargs)


class TaskForm(forms.ModelForm):

    user_desc = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}), label=_('Usuario'))
    lang_desc = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}), label=_('Idioma'))

    def __init__(self, instance=None, *args, **kwargs):
        self.base_fields['user_desc'].initial = instance.user.user.username
        self.base_fields['lang_desc'].initial = instance.language.name
        super().__init__(instance=instance, *args, **kwargs)

    class Meta:
        model = TransTask
        fields = ('user_desc', 'lang_desc', 'user', 'language', 'object_name', 'object_class', 'object_pk',
                  'object_field_label', 'number_of_words', 'object_field_value',
                  'object_field_value_translation', 'done')
        widgets = {
            'object_name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'object_class': forms.TextInput(attrs={'readonly': 'readonly'}),
            'object_pk': forms.TextInput(attrs={'readonly': 'readonly'}),
            'object_field_label': forms.TextInput(attrs={'readonly': 'readonly'}),
            'number_of_words': forms.TextInput(attrs={'readonly': 'readonly'}),
            'object_field_value': forms.Textarea(attrs={'readonly': 'readonly'}),
            'user': forms.HiddenInput(attrs={'readonly': 'readonly'}),
            'language': forms.HiddenInput(attrs={'readonly': 'readonly'}),
        }
