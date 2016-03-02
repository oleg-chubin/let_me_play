# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_auth', '0002_auto_20151202_2116'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.ImageField(upload_to='avatars', verbose_name='image', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='cell_phone',
            field=models.CharField(max_length=16, verbose_name='cell phone', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='sex',
            field=models.IntegerField(default=3, choices=[(1, 'Male'), (2, 'Female'), (3, 'Not specified')]),
            preserve_default=True,
        ),
    ]
