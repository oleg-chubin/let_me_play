# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_climb', '0003_auto_20160730_1429'),
    ]

    operations = [
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('route_color', models.IntegerField(choices=[(1, 'Red'), (2, 'Orange'), (3, 'Yellow'), (4, 'Green'), (5, 'Blue'), (6, 'Indigo'), (7, 'Violet'), (8, 'Not specified')], default=8)),
                ('route_score', models.IntegerField(default=0)),
            ],
        ),
    ]
