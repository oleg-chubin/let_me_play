# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_app', '0011_coachrecommendation_indexparametr_visitindex'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='staff',
        ),
        migrations.RemoveField(
            model_name='staffprofile',
            name='followable_ptr',
        ),
        migrations.AlterField(
            model_name='staffprofile',
            name='user',
            field=models.OneToOneField(serialize=False, primary_key=True, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
