# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transmanager', '0002_transitemlanguage'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='transitemlanguage',
            options={'verbose_name': 'Idiomas por item', 'verbose_name_plural': 'Idiomas por item'},
        ),
        migrations.AlterField(
            model_name='transitemlanguage',
            name='content_type',
            field=models.ForeignKey(to='contenttypes.ContentType', verbose_name='Modelo'),
        ),
        migrations.AlterField(
            model_name='transitemlanguage',
            name='languages',
            field=models.ManyToManyField(verbose_name='Idiomas', to='transmanager.TransLanguage', help_text='Idiomas por defecto del item'),
        ),
        migrations.AlterField(
            model_name='transitemlanguage',
            name='object_id',
            field=models.PositiveIntegerField(verbose_name='Identificador'),
        ),
    ]
