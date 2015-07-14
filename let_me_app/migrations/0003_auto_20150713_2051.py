# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import osm_field.fields
import osm_field.validators


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_app', '0002_auto_20150705_1554'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='location',
            field=osm_field.fields.OSMField(default=1, lon_field='location_lon', lat_field='location_lat'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='site',
            name='location_lat',
            field=osm_field.fields.LatitudeField(validators=[osm_field.validators.validate_latitude], default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='site',
            name='location_lon',
            field=osm_field.fields.LongitudeField(validators=[osm_field.validators.validate_longitude], default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='court',
            name='admin_group',
            field=models.ForeignKey(to='auth.Group', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='court',
            name='description',
            field=models.TextField(verbose_name='Description'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='site',
            name='address',
            field=models.TextField(verbose_name='Address'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='site',
            name='description',
            field=models.TextField(verbose_name='Description'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='peeper',
            unique_together=set([('followable', 'user')]),
        ),
    ]
