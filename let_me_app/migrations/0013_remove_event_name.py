# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_app', '0012_auto_20160126_2209'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='name',
        ),
    ]
