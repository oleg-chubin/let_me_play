# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_app', '0016_auto_20160228_1615'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coolnessrate',
            name='value',
            field=models.IntegerField(choices=[(1, 'weaker'), (2, 'bit_weaker'), (3, 'same'), (4, 'bit_stronger'), (5, 'stronger')], default=3),
        ),
    ]
