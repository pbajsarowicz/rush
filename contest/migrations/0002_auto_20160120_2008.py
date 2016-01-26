# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-20 19:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rushuser',
            name='date_joined',
            field=models.DateTimeField(auto_now_add=True, verbose_name='data do\u0142\u0105czenia'),
        ),
        migrations.AlterField(
            model_name='rushuser',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='adres email'),
        ),
        migrations.AlterField(
            model_name='rushuser',
            name='first_name',
            field=models.CharField(max_length=32, verbose_name='imi\u0119'),
        ),
        migrations.AlterField(
            model_name='rushuser',
            name='is_active',
            field=models.BooleanField(default=False, verbose_name='u\u017cytkownik zaakceptowany'),
        ),
        migrations.AlterField(
            model_name='rushuser',
            name='last_name',
            field=models.CharField(max_length=32, verbose_name='nazwisko'),
        ),
        migrations.AlterField(
            model_name='rushuser',
            name='organization_address',
            field=models.CharField(max_length=255, verbose_name='adres organizacji'),
        ),
        migrations.AlterField(
            model_name='rushuser',
            name='organization_name',
            field=models.CharField(blank=True, max_length=255, verbose_name='nazwa organizacji'),
        ),
        migrations.AlterField(
            model_name='rushuser',
            name='username',
            field=models.CharField(max_length=64, unique=True, verbose_name='nazwa u\u017cytkownika'),
        ),
    ]
