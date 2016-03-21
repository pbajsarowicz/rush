# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-19 16:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0009_auto_20160319_1702'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='adres email')),
                ('website', models.URLField(blank=True, verbose_name='strona internetowa szko\u0142y/klubu')),
                ('phone_number', models.CharField(blank=True, max_length=9, verbose_name='numer telefonu')),
            ],
        ),
        migrations.RemoveField(
            model_name='club',
            name='id',
        ),
        migrations.RemoveField(
            model_name='school',
            name='id',
        ),
        migrations.AddField(
            model_name='club',
            name='contact',
            field=models.OneToOneField(default=999999999, on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='contest.Contact'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='school',
            name='contact',
            field=models.OneToOneField(default=999999999, on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='contest.Contact'),
            preserve_default=False,
        ),
    ]
