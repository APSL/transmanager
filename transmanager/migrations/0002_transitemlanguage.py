# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('transmanager', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransItemLanguage',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('languages', models.ManyToManyField(to='transmanager.TransLanguage', verbose_name='Idiomas', help_text='Idiomas por defecto del modelo')),
            ],
            options={
                'verbose_name_plural': 'Idiomas por items',
                'verbose_name': 'Idiomas por item',
            },
        ),
    ]
