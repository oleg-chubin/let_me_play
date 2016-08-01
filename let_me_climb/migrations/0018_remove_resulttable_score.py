# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_climb', '0017_participant_group'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='resulttable',
            name='score',
        ),
    ]
