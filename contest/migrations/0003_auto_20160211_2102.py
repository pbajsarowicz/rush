# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-11 20:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0002_auto_20160210_2202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rushuser',
            name='club',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contest.Club'),
        ),
    ]