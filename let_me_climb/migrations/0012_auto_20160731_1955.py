# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_climb', '0011_resulttable_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resulttable',
            name='route',
            field=models.ManyToManyField(blank=True, to='let_me_climb.Route'),
        ),
    ]
