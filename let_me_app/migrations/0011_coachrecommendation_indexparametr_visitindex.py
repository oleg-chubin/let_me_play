# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_app', '0010_auto_20160121_0831'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoachRecommendation',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('recommendation', models.TextField(verbose_name='Description', default='', max_length=1024)),
                ('status', models.IntegerField(default=1, choices=[(1, 'Active'), (2, 'Outdated'), (3, 'Canceled')])),
                ('coach', models.ForeignKey(to='let_me_app.StaffProfile')),
                ('visit', models.ForeignKey(to='let_me_app.Visit')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IndexParametr',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=256)),
                ('units', models.CharField(verbose_name='units', max_length=16)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VisitIndex',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('value', models.FloatField(verbose_name='Value')),
                ('parametr', models.ForeignKey(to='let_me_app.IndexParametr')),
                ('visit', models.ForeignKey(to='let_me_app.Visit')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
