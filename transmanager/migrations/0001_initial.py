# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TransApplicationLanguage',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('application', models.CharField(unique=True, verbose_name='Aplicación', max_length=100)),
            ],
            options={
                'verbose_name': 'Idiomas por aplicación',
                'verbose_name_plural': 'Idiomas por aplicaciones',
            },
        ),
        migrations.CreateModel(
            name='TransLanguage',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('code', models.CharField(verbose_name='Código', max_length=2, help_text='Código ISO del idioma')),
                ('name', models.CharField(verbose_name='Nombre', max_length=40)),
                ('main_language', models.BooleanField(verbose_name='Idioma principal', default=False, help_text='¿Es el idioma principal?')),
            ],
            options={
                'verbose_name': 'Idioma',
                'verbose_name_plural': 'Idiomas',
            },
        ),
        migrations.CreateModel(
            name='TransModelLanguage',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('model', models.CharField(unique=True, verbose_name='Modelo', max_length=100)),
                ('languages', models.ManyToManyField(to='transmanager.TransLanguage', verbose_name='Idiomas', help_text='Idiomas por defecto del modelo')),
            ],
            options={
                'verbose_name': 'Idiomas por modelo',
                'verbose_name_plural': 'Idiomas por modelos',
            },
        ),
        migrations.CreateModel(
            name='TransTask',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('object_class', models.CharField(verbose_name='Clase', max_length=100, help_text='Clase del objeto')),
                ('object_pk', models.IntegerField(verbose_name='Clave', help_text='Clave primária del objeto')),
                ('date_creation', models.DateTimeField(verbose_name='Fecha creación', auto_now_add=True)),
                ('date_modification', models.DateTimeField(verbose_name='Fecha modificación', auto_now=True)),
                ('notified', models.BooleanField(verbose_name='Notificada', default=False, help_text='Si la tarea ya ha sido notificada o no al usuario')),
                ('date_notified', models.DateTimeField(blank=True, verbose_name='Fecha notificacion', null=True)),
                ('object_name', models.CharField(verbose_name='Nombre objeto', max_length=200)),
                ('object_field', models.CharField(verbose_name='Nombre campo', max_length=200, help_text='Nombre del atributo en el modelo')),
                ('object_field_label', models.CharField(verbose_name='Descripción campo', max_length=200, help_text='Etiqueta del campo')),
                ('object_field_value', models.TextField(verbose_name='Valor', help_text='Valor del campo en el idioma principal')),
                ('object_field_value_translation', models.TextField(blank=True, verbose_name='Valor traducido', null=True, help_text='Valor traducido del campo en el idioma principal')),
                ('number_of_words', models.IntegerField(verbose_name='Número palabras', default=0, help_text='Número de palabras a traducir en el idioma original')),
                ('done', models.BooleanField(verbose_name='Hecho', default=False)),
                ('language', models.ForeignKey(to='transmanager.TransLanguage', verbose_name='Idioma')),
            ],
            options={
                'verbose_name_plural': 'Tareas',
                'verbose_name': 'Tarea',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='TransUser',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('active', models.BooleanField(verbose_name='Activo', default=True)),
                ('languages', models.ManyToManyField(to='transmanager.TransLanguage', verbose_name='Idiomas')),
                ('user', models.OneToOneField(related_name='translator_user', to=settings.AUTH_USER_MODEL, verbose_name='Usuario')),
            ],
            options={
                'verbose_name': 'Traductor',
                'verbose_name_plural': 'Traductores',
            },
        ),
        migrations.AddField(
            model_name='transtask',
            name='user',
            field=models.ForeignKey(related_name='tasks', to='transmanager.TransUser', verbose_name='Usuario'),
        ),
        migrations.AddField(
            model_name='transapplicationlanguage',
            name='languages',
            field=models.ManyToManyField(to='transmanager.TransLanguage', verbose_name='Idiomas', help_text='Idiomas por defecto de la aplicación'),
        ),
    ]
