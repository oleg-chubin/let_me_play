# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_climb', '0007_auto_20160730_1901'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResultTable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('participant', models.ForeignKey(to='let_me_climb.Participant')),
                ('route', models.ManyToManyField(to='let_me_climb.Route')),
            ],
        ),
    ]
