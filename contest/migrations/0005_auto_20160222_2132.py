# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-22 20:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0004_auto_20160220_1358'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contest',
            name='for_who',
        ),
        migrations.AddField(
            model_name='contest',
            name='age_max',
            field=models.SmallIntegerField(default=99),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contest',
            name='age_min',
            field=models.SmallIntegerField(default=10),
            preserve_default=False,
        ),
    ]
