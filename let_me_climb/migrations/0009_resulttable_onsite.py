# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_climb', '0008_resulttable'),
    ]

    operations = [
        migrations.AddField(
            model_name='resulttable',
            name='onsite',
            field=models.ManyToManyField(to='let_me_climb.Route', related_name='onsite'),
        ),
    ]
