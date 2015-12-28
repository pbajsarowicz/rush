# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-28 18:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RushUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('login', models.CharField(max_length=30, unique=True, verbose_name='Login u\u017cytkownika')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Adres email')),
                ('first_name', models.CharField(max_length=30, verbose_name='Imi\u0119')),
                ('last_name', models.CharField(max_length=30, verbose_name='Nazwisko')),
                ('organization_name', models.CharField(max_length=30, verbose_name='Nazwa organizacji')),
                ('organization_address', models.CharField(max_length=30, verbose_name='Adres organizacji')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='Data do\u0142\u0105czenia')),
                ('is_active', models.BooleanField(default=False)),
                ('is_admin', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
