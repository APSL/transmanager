How it works
============
TransManager its based on the handling pre_save django signal. This allow to detect the changes done in
the translatable fields of a model.

The system has to be configured as follows, every model has to have set the languages we want the translations to.
We can set the languages per app as well, in this case if a model has no languages configured we'll take
the model app specified languages. Besides, every language defined on the TransManager admin has to have
an user assigned. An user can have more than one languages assigned. If there is a language without a user,
the translations tasks will not be created.


Creation of new registry
------------------------
When a new registry is created we create a new translation task for every translatable not empty field in
every language configured for the model we're the new registry.


Modification of a registry
--------------------------
When we modify a register, we will create a translation task for every modified translatable field
in the original language.


Translating the tasks
---------------------
Once the tasks are created they have to be translated. When we translate the task, having the main
language original text as reference in the edition form, at the moment of saving the task the main
object will be updated. This way it have the advantage that the translator user does not have to have
access to the main content models, avoiding undesired deletions or modifications on these main models.
