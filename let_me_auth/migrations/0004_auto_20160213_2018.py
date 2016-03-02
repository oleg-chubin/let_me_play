# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_auth', '0003_auto_20160130_1544'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationSettings',
            fields=[
                ('sms_notifications', models.BooleanField(verbose_name='Use sms for notifications')),
                ('email_notifications', models.BooleanField(verbose_name='Use email for notifications')),
                ('lang', models.CharField(verbose_name='cell phone', max_length=18)),
                ('user', models.OneToOneField(primary_key=True, to=settings.AUTH_USER_MODEL, serialize=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='user',
            name='cell_phone_is_valid',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
