# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_app', '0018_galleryvideo'),
    ]

    operations = [
        migrations.AddField(
            model_name='court',
            name='name',
            field=models.CharField(default='Court', max_length=128),
            preserve_default=False,
        ),
    ]
