# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-09 16:00
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0005_rushuser_has_setted_password'),
    ]

    operations = [
        migrations.RenameField(
            model_name='rushuser',
            old_name='has_setted_password',
            new_name='is_set_password',
        ),
    ]
