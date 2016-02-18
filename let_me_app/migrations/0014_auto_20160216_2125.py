# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_app', '0013_remove_event_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='geo_line',
            field=django.contrib.gis.db.models.fields.LineStringField(srid=4326, verbose_name='Geo line', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='court',
            name='site',
            field=models.ForeignKey(to='let_me_app.Site', related_name='court_set'),
        ),
    ]
