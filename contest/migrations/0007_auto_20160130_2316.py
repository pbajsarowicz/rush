# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-30 22:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0006_auto_20160130_2315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='club',
            name='code',
            field=models.CharField(max_length=5, verbose_name='kod klubu'),
        ),
    ]
