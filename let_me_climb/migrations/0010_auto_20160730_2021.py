# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_climb', '0009_resulttable_onsite'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='birth_date',
            field=models.DateField(default=datetime.datetime(1970, 1, 1, 0, 0), verbose_name='birth date'),
        ),
        migrations.AlterField(
            model_name='resulttable',
            name='onsite',
            field=models.ManyToManyField(related_name='onsite', blank=True, to='let_me_climb.Route'),
        ),
    ]
