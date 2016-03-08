# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_auth', '0006_auto_20160216_2125'),
    ]

    operations = [
        migrations.AddField(
            model_name='confirmationcodes',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2016, 3, 8, 13, 47, 26, 759005, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='notificationsettings',
            name='email_notifications',
            field=models.BooleanField(verbose_name='Use email for notifications', choices=[(True, 'Email Notifications Enabled'), (False, 'Email Notifications Disabled')], default=False),
        ),
        migrations.AlterField(
            model_name='notificationsettings',
            name='sms_notifications',
            field=models.BooleanField(verbose_name='Use sms for notifications', choices=[(True, 'Sms Notifications Enabled'), (False, 'Sms Notifications Disabled')], default=False),
        ),
    ]
