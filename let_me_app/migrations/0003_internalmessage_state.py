# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_app', '0002_auto_20150222_1502'),
    ]

    operations = [
        migrations.AddField(
            model_name='internalmessage',
            name='state',
            field=models.IntegerField(choices=[(1, 'Read'), (2, 'Unread')], default=2),
            preserve_default=True,
        ),
    ]
