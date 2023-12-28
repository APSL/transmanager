# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2023-11-23 13:18
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import transmanager.models
import uuid


class Migration(migrations.Migration):

    replaces = [('transmanager', '0001_initial'), ('transmanager', '0002_transitemlanguage'), ('transmanager', '0003_auto_20160513_2151'), ('transmanager', '0004_transtask_content_type'), ('transmanager', '0005_transuserexport')]

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransApplicationLanguage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('application', models.CharField(max_length=100, unique=True, verbose_name='Aplicación')),
            ],
            options={
                'verbose_name': 'Idiomas por aplicación',
                'verbose_name_plural': 'Idiomas por aplicaciones',
            },
        ),
        migrations.CreateModel(
            name='TransLanguage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(help_text='Código ISO del idioma', max_length=2, verbose_name='Código')),
                ('name', models.CharField(max_length=40, verbose_name='Nombre')),
                ('main_language', models.BooleanField(default=False, help_text='¿Es el idioma principal?', verbose_name='Idioma principal')),
            ],
            options={
                'verbose_name': 'Idioma',
                'verbose_name_plural': 'Idiomas',
            },
        ),
        migrations.CreateModel(
            name='TransModelLanguage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model', models.CharField(max_length=100, unique=True, verbose_name='Modelo')),
                ('languages', models.ManyToManyField(help_text='Idiomas por defecto del modelo', to='transmanager.TransLanguage', verbose_name='Idiomas')),
            ],
            options={
                'verbose_name': 'Idiomas por modelo',
                'verbose_name_plural': 'Idiomas por modelos',
            },
        ),
        migrations.CreateModel(
            name='TransTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_class', models.CharField(help_text='Clase del objeto', max_length=100, verbose_name='Clase')),
                ('object_pk', models.IntegerField(help_text='Clave primária del objeto', verbose_name='Clave')),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='Fecha creación')),
                ('date_modification', models.DateTimeField(auto_now=True, verbose_name='Fecha modificación')),
                ('notified', models.BooleanField(default=False, help_text='Si la tarea ya ha sido notificada o no al usuario', verbose_name='Notificada')),
                ('date_notified', models.DateTimeField(blank=True, null=True, verbose_name='Fecha notificacion')),
                ('object_name', models.CharField(max_length=200, verbose_name='Nombre objeto')),
                ('object_field', models.CharField(help_text='Nombre del atributo en el modelo', max_length=200, verbose_name='Nombre campo')),
                ('object_field_label', models.CharField(help_text='Etiqueta del campo', max_length=200, verbose_name='Descripción campo')),
                ('object_field_value', models.TextField(help_text='Valor del campo en el idioma principal', verbose_name='Valor')),
                ('object_field_value_translation', models.TextField(blank=True, help_text='Valor traducido del campo en el idioma principal', null=True, verbose_name='Valor traducido')),
                ('number_of_words', models.IntegerField(default=0, help_text='Número de palabras a traducir en el idioma original', verbose_name='Número palabras')),
                ('done', models.BooleanField(default=False, verbose_name='Hecho')),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='transmanager.TransLanguage', verbose_name='Idioma')),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': 'Tarea',
                'verbose_name_plural': 'Tareas',
            },
        ),
        migrations.CreateModel(
            name='TransUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True, verbose_name='Activo')),
                ('languages', models.ManyToManyField(to='transmanager.TransLanguage', verbose_name='Idiomas')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='translator_user', to=settings.AUTH_USER_MODEL, verbose_name='Usuario')),
            ],
            options={
                'verbose_name': 'Traductor',
                'verbose_name_plural': 'Traductores',
            },
        ),
        migrations.AddField(
            model_name='transtask',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='transmanager.TransUser', verbose_name='Usuario'),
        ),
        migrations.AddField(
            model_name='transapplicationlanguage',
            name='languages',
            field=models.ManyToManyField(help_text='Idiomas por defecto de la aplicación', to='transmanager.TransLanguage', verbose_name='Idiomas'),
        ),
        migrations.CreateModel(
            name='TransItemLanguage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField(verbose_name='Identificador')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType', verbose_name='Modelo')),
                ('languages', models.ManyToManyField(help_text='Idiomas por defecto del item', to='transmanager.TransLanguage', verbose_name='Idiomas')),
            ],
            options={
                'verbose_name': 'Idiomas por item',
                'verbose_name_plural': 'Idiomas por item',
            },
        ),
        migrations.AddField(
            model_name='transtask',
            name='content_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType', verbose_name='Modelo'),
        ),
        migrations.CreateModel(
            name='TransUserExport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, max_length=255, null=True, upload_to=transmanager.models.TransUserExport.upload_path)),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='creation date')),
                ('uuid', models.UUIDField(default=uuid.uuid4, unique=True, verbose_name='Unique identifier')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exports', to=settings.AUTH_USER_MODEL, verbose_name='usuario')),
            ],
            options={
                'verbose_name': 'User export',
                'verbose_name_plural': 'User exports',
            },
        ),
    ]
