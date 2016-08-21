# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-08-21 15:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0007_auto_20160815_1903'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContestantScore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_result', models.FloatField(blank=True, null=True, verbose_name='Najlepszy czas')),
            ],
        ),
        migrations.CreateModel(
            name='ContestStyleDistances',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Distance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=16, verbose_name='Dystans')),
            ],
        ),
        migrations.CreateModel(
            name='Style',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='Styl')),
            ],
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='styles',
        ),
        migrations.RemoveField(
            model_name='contest',
            name='styles',
        ),
        migrations.AddField(
            model_name='conteststyledistances',
            name='distance',
            field=models.ManyToManyField(to='contest.Distance'),
        ),
        migrations.AddField(
            model_name='conteststyledistances',
            name='style',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contest.Style'),
        ),
        migrations.AddField(
            model_name='contestantscore',
            name='contestant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contest.Contestant'),
        ),
        migrations.AddField(
            model_name='contestantscore',
            name='distance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contest.Distance'),
        ),
        migrations.AddField(
            model_name='contestantscore',
            name='style',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contest.Style'),
        ),
        migrations.AddField(
            model_name='contest',
            name='styles',
            field=models.ManyToManyField(to='contest.ContestStyleDistances'),
        ),
        migrations.AlterUniqueTogether(
            name='contestantscore',
            unique_together=set([('contestant', 'style', 'distance')]),
        ),
    ]