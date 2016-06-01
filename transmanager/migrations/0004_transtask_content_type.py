# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('transmanager', '0003_auto_20160513_2151'),
    ]

    operations = [
        migrations.AddField(
            model_name='transtask',
            name='content_type',
            field=models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True, verbose_name='Modelo'),
        ),
    ]
