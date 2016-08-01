# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_climb', '0015_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='group_age',
            field=models.CharField(verbose_name='group age', default='', max_length=30),
        ),
    ]
