# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_app', '0004_auto_20150628_1552'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, 'Pending'), (2, 'Completed'), (3, 'Canceled')]),
            preserve_default=True,
        ),
    ]
