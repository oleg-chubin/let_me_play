# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_app', '0008_auto_20150809_1341'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventStaff',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('event', models.ForeignKey(to='let_me_app.Event')),
                ('invoice', models.ForeignKey(null=True, blank=True, to='let_me_app.Invoice')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StaffRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(verbose_name='name', default='', max_length=128)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='eventstaff',
            name='role',
            field=models.ForeignKey(to='let_me_app.StaffRole'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventstaff',
            name='staff',
            field=models.ForeignKey(to='let_me_app.StaffProfile'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='activitytype',
            name='title',
            field=models.CharField(verbose_name='title', max_length=128),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='application',
            name='comment',
            field=models.TextField(verbose_name='comment', default='', max_length=256),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='equipment',
            name='name',
            field=models.CharField(verbose_name='name', max_length=256),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='description',
            field=models.TextField(verbose_name='Description', default='', max_length=1024),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='name',
            field=models.CharField(verbose_name='name', default='', max_length=128),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='galleryimage',
            name='note',
            field=models.CharField(verbose_name='note', default='just a picture', max_length=128),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='inventory',
            name='amount',
            field=models.IntegerField(verbose_name='amount'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='inventorylist',
            name='name',
            field=models.CharField(verbose_name='name', max_length=256),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='proposal',
            name='comment',
            field=models.TextField(verbose_name='comment', default='', max_length=256),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='site',
            name='geo_point',
            field=django.contrib.gis.db.models.fields.PointField(verbose_name='Geo point', null=True, blank=True, srid=4326),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='site',
            name='name',
            field=models.CharField(verbose_name='name', max_length=128),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='staffprofile',
            name='description',
            field=models.TextField(verbose_name='description'),
            preserve_default=True,
        ),
    ]
