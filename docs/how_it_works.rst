How it works
============
TransManager its based on the handling pre_save django signal. This allow to detect the changes done in
the translatable fields of a model.

The system has to be configured as follows, we have to create the language we want the translations into.
Then every multilang model has to have set the languages we want the translations into.
We can set the languages per app as well, in this case if a model has no languages configured we'll take
the model app specified languages. Besides, every language defined on the TransManager admin has to have
an user assigned. An user can have more than one languages assigned. If there is a language without a user,
the translations tasks will not be created.


Creation of new record
----------------------
When a new record is created we create a new translation task for every translatable not empty field in
every language configured for the model we're the new record.


Modification of a record
------------------------
When we modify a register, we will create a translation task for every modified translatable field
in the original language.


Translating the tasks
---------------------
Once the tasks are created they have to be translated. When we translate the task, having the main
language original text as reference in the edition form, at the moment of saving the task the main
object will be updated. This way it have the advantage that the translator user does not have to have
access to the main content models, avoiding undesired deletions or modifications on these main models.


Translation a specific records
------------------------------
In Transmanager, every time we insert or modify a content in the main language, a task is generated
for every language defined in the model we are editing.

Nevertheless, we have the possibility to order a translation in one or more languages ONLY
for an specific record of the model, even if the language(s) are not set by default in the model we're editing.
This can be done throught the "Translations menu" that we can add to our edit form template via TransManager template tag

.. code-block:: python

    {% if object %}
        {% show_list_translations object %}
    {% endif %}

.. image:: images/translation_menu.png

From the translation menu, we can order a translation for one o more language for the specific item we're editing.
We can also delete the translation tasks ordered before in one o more languages for the specific item we're editing.
We see as well the default languages for the model (the languages in which the translations tasks will be generated
automatically), these default language that have the grey background.

Finally, you can see the default languages for the specific item as well.


Child models
^^^^^^^^^^^^
When working with specific records, it can happen that we edit a form that includes a formset. The records of
the formset are children of the main form specific record. When we order a translation task for the main specific
record we order as well the translation tasks for the records of the related formset.

In order to achieve the behaviour described above, we have to add the method :code:`get_parent` to the formset model, e.g.:

.. code-block:: python

    class CardCharacteristic(TranslatableModel):

        card = models.ForeignKey(Card, verbose_name=_('Card Experience'), related_name='characteristics')
        type = models.ForeignKey(CardCharacteristicType, verbose_name=_('Tipo'))
        translations = TranslatedFields(
            value=models.TextField(verbose_name=_('Valor'))
        )

        def __str__(self):
            try:
                return '{} - {} - {}'.format(self.card_id, self.type, self.lazy_translation_getter('value'))
            except AttributeError:
                return '[{}]'.format(self.pk)

        class Meta:
            ordering = ('card', 'type')
            verbose_name = _('Característica Card Experience')
            verbose_name_plural = _('Características Card Experience')

        def get_parent(self):
            return self.card


This way when we order a translation task, the generation process will know which the children model is.


Enabling/Disabling a specific record translations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
When working with specific records, it can happen that we work on the content in several times and we don't want to
generate the translation tasks every time we save the record. In order to accomplish this behaviour, we can add an
attribute to the model we're editing that allows us to know if the record is "enabled" or "disabled". **Enabled** means
the edition of the record is finished and ready to generate the translation tasks. **Disabled** means the record is not
ready yet and we don't want the translation tasks to be generated.

The name of the model attribute can be configured in the settings, via the enabled_ constant.


