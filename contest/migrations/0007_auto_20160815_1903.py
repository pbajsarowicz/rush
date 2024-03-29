# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-08-15 17:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0006_contestfiles'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contestant',
            name='school',
            field=models.CharField(blank=True, choices=[(None, 'Wybierz rodzaj szko\u0142y'), ('P', 'Szko\u0142a podstawowa'), ('G', 'Gimnazjum'), ('S', 'Szko\u0142a \u015brednia')], max_length=1, null=True, verbose_name='rodzaj szko\u0142y'),
        ),
        migrations.AlterField(
            model_name='rushuser',
            name='organization_address',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Adres'),
        ),
        migrations.AlterField(
            model_name='rushuser',
            name='organization_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Nazwa'),
        ),
    ]
