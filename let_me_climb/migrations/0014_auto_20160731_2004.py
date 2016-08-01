# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_climb', '0013_auto_20160731_2003'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resulttable',
            name='onsite',
            field=models.ManyToManyField(to='let_me_climb.Route', blank=True, related_name='onsite'),
        ),
    ]
