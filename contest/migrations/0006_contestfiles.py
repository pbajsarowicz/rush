# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-08-13 14:56
from __future__ import unicode_literals

import contest.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0005_contest_results'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContestFiles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_uploaded', models.DateTimeField(auto_now_add=True)),
                ('contest_file', models.FileField(upload_to=contest.models.contest_directory_path, verbose_name='Pliki')),
                ('name', models.CharField(default='', max_length=255, verbose_name='Nazwa pliku')),
                ('contest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contest.Contest')),
                ('uploaded_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]