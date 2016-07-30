# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_climb', '0010_auto_20160730_2021'),
    ]

    operations = [
        migrations.AddField(
            model_name='resulttable',
            name='score',
            field=models.IntegerField(default=0),
        ),
    ]
