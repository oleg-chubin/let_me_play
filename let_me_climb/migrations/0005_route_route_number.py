# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_climb', '0004_route'),
    ]

    operations = [
        migrations.AddField(
            model_name='route',
            name='route_number',
            field=models.IntegerField(verbose_name='route number', default=1),
        ),
    ]
