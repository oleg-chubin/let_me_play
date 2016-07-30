# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_climb', '0002_auto_20160730_1415'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='city',
            field=models.CharField(verbose_name='city', default='Sevastopol', max_length=30),
        ),
        migrations.AddField(
            model_name='participant',
            name='country',
            field=models.CharField(verbose_name='country', default='Russia', max_length=30),
        ),
    ]
