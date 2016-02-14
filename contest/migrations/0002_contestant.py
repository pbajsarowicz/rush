# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-14 15:14
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contestant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=32, verbose_name='imi\u0119')),
                ('last_name', models.CharField(max_length=32, verbose_name='nazwisko')),
                ('gender', models.CharField(choices=[(None, 'Wybierz p\u0142e\u0107'), ('F', 'Kobieta'), ('M', 'M\u0119\u017cczyzna')], max_length=1, verbose_name='p\u0142e\u0107')),
                ('age', models.IntegerField(verbose_name='wiek')),
                ('school', models.CharField(max_length=255, verbose_name='rodzaj szko\u0142y')),
                ('styles_distances', models.CharField(max_length=255, verbose_name='style i dystanse')),
                ('moderator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
