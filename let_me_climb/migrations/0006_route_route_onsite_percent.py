# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_climb', '0005_route_route_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='route',
            name='route_onsite_percent',
            field=models.IntegerField(default=0),
        ),
    ]
