# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_climb', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='participant',
            name='user',
        ),
        migrations.AddField(
            model_name='participant',
            name='avatar',
            field=models.ImageField(verbose_name='image', blank=True, upload_to='avatars'),
        ),
        migrations.AddField(
            model_name='participant',
            name='birth_date',
            field=models.DateField(default=datetime.datetime(1950, 1, 1, 0, 0), verbose_name='birth date'),
        ),
        migrations.AddField(
            model_name='participant',
            name='email',
            field=models.EmailField(verbose_name='email address', blank=True, unique=True, max_length=254),
        ),
        migrations.AddField(
            model_name='participant',
            name='first_name',
            field=models.CharField(default='', verbose_name='first name', max_length=30),
        ),
        migrations.AddField(
            model_name='participant',
            name='last_name',
            field=models.CharField(default='', verbose_name='last name', max_length=30),
        ),
        migrations.AddField(
            model_name='participant',
            name='middle_name',
            field=models.CharField(verbose_name='middle name', blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='participant',
            name='phone',
            field=models.CharField(verbose_name='cell phone', blank=True, max_length=16),
        ),
        migrations.AddField(
            model_name='participant',
            name='sex',
            field=models.IntegerField(choices=[(1, 'Male'), (2, 'Female'), (3, 'Not specified')], default=3),
        ),
        migrations.AddField(
            model_name='participant',
            name='sport_level',
            field=models.IntegerField(choices=[(1, 'Amateur'), (2, 'Sport rank #3'), (3, 'Sport rank #2'), (4, 'Sport rank #1'), (5, 'Sport rank KMS'), (6, 'Sport rank MS'), (7, 'Sport rank MSMK'), (8, 'Not specified')], default=8),
        ),
    ]
