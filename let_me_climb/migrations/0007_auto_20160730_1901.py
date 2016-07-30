# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_climb', '0006_route_route_onsite_percent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='route',
            name='route_onsite_percent',
            field=models.IntegerField(verbose_name='onsite %', default=10),
        ),
    ]
