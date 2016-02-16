# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_auth', '0004_auto_20160213_2018'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfirmationCodes',
            fields=[
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=8, verbose_name='confirmation code')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='notificationsettings',
            name='lang',
            field=models.CharField(max_length=18, verbose_name='language'),
            preserve_default=True,
        ),
    ]
