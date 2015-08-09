# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_app', '0007_auto_20150723_2238'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='start_at',
            field=models.DateTimeField(verbose_name='date started', db_index=True),
            preserve_default=True,
        ),
    ]
