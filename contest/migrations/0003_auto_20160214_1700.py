# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-14 16:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0002_contestant'),
    ]

    operations = [
        migrations.CreateModel(
            name='Club',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='nazwa klubu')),
                ('code', models.IntegerField(default=0, verbose_name='kod klubu')),
            ],
        ),
        migrations.AddField(
            model_name='rushuser',
            name='club',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contest.Club'),
        ),
    ]