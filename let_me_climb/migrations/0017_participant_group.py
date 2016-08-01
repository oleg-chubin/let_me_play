# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_climb', '0016_group_group_age'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='group',
            field=models.ForeignKey(default=1, to='let_me_climb.Group'),
            preserve_default=False,
        ),
    ]
