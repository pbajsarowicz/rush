# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-08-01 20:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0004_contestfiles'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contestfiles',
            name='docfile1',
        ),
        migrations.RemoveField(
            model_name='contestfiles',
            name='docfile2',
        ),
        migrations.RemoveField(
            model_name='contestfiles',
            name='docfile3',
        ),
        migrations.RemoveField(
            model_name='contestfiles',
            name='docfile4',
        ),
        migrations.AddField(
            model_name='contestfiles',
            name='docfile',
            field=models.FileField(default='brak', upload_to='trolollo/', verbose_name='Pliki'),
        ),
    ]
