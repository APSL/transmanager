Commands
========
There are several commands that help to keep clean and keen the translation tasks list.


Delete orphan tasks
-------------------
This commands deletes the tasks that no longer have a related main object.

:code:`python manage.py delete_orphan_tasks`


Generate tasks
--------------
Generate the translation tasks from the existing data.

:code:`python manage.py generate_tasks`


Notify translators
------------------
Command that notifies the translators of pending translation tasks.
Its a command that, if we want our translator users notified of the pending tasks,
we have to cron in order to send the nofitication email to them.

:code:`python manage.py notify_translators`


Update number of words
----------------------
Update the number of words to translate in every task. It counts the number of words of the original text to translate.

:code:`python manage.py update_number_of_words`
