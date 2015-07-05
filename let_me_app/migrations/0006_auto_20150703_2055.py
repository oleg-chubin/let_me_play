# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_app', '0005_event_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatparticipant',
            name='last_seen',
            field=models.DateTimeField(default=datetime.datetime(2015, 7, 3, 20, 55, 54, 620125, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='visit',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, 'Pending'), (2, 'Completed'), (3, 'Canceled'), (4, 'Declined'), (5, 'Missed')]),
            preserve_default=True,
        ),
    ]
