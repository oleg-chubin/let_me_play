# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_app', '0009_auto_20151207_1857'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='preliminary_price',
            field=models.IntegerField(verbose_name='Preliminary price', default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='eventstaff',
            name='event',
            field=models.ForeignKey(verbose_name='event', to='let_me_app.Event'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='eventstaff',
            name='invoice',
            field=models.ForeignKey(blank=True, null=True, verbose_name='invoice', to='let_me_app.Invoice'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='eventstaff',
            name='role',
            field=models.ForeignKey(verbose_name='role', to='let_me_app.StaffRole'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='eventstaff',
            name='staff',
            field=models.ForeignKey(verbose_name='staff', to='let_me_app.StaffProfile'),
            preserve_default=True,
        ),
    ]
