# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_app', '0003_auto_20150713_2051'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='site',
            name='location',
        ),
        migrations.RemoveField(
            model_name='site',
            name='location_lat',
        ),
        migrations.RemoveField(
            model_name='site',
            name='location_lon',
        ),
        migrations.AddField(
            model_name='site',
            name='geo_point',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326),
            preserve_default=True,
        ),
    ]
