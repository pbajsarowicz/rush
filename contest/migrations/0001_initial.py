# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-10 20:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


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
                ('username', models.CharField(max_length=64, unique=True, verbose_name='nazwa u\u017cytkownika')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='adres email')),
                ('first_name', models.CharField(max_length=32, verbose_name='imi\u0119')),
                ('last_name', models.CharField(max_length=32, verbose_name='nazwisko')),
                ('organization_name', models.CharField(blank=True, max_length=255, verbose_name='nazwa organizacji')),
                ('organization_address', models.CharField(max_length=255, verbose_name='adres organizacji')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='data do\u0142\u0105czenia')),
                ('is_active', models.BooleanField(default=False, verbose_name='u\u017cytkownik zaakceptowany')),
                ('is_admin', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Club',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='nazwa klubu, max_length=255')),
                ('code', models.IntegerField(default=0, verbose_name='kod klubu')),
            ],
        ),
        migrations.AddField(
            model_name='rushuser',
            name='club',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contest.Club'),
        ),
    ]
