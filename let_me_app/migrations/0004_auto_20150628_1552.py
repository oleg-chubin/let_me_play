# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_app', '0003_auto_20150531_1416'),
    ]

    operations = [
        migrations.AddField(
            model_name='visit',
            name='status',
            field=models.IntegerField(choices=[(1, 'Pending'), (2, 'Completed'), (3, 'Canceled'), (4, 'Declined')], default=1),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='staff',
            field=models.ManyToManyField(to='let_me_app.StaffProfile', blank=True),
            preserve_default=True,
        ),
    ]
