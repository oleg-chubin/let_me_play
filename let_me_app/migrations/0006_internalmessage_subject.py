# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_app', '0005_auto_20150715_1939'),
    ]

    operations = [
        migrations.AddField(
            model_name='internalmessage',
            name='subject',
            field=models.ForeignKey(to='let_me_app.Followable', null=True, blank=True),
            preserve_default=True,
        ),
    ]
