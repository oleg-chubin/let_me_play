# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_auth', '0005_auto_20160215_1706'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificationsettings',
            name='email_notifications',
            field=models.BooleanField(verbose_name='Use email for notifications', default=False),
        ),
        migrations.AlterField(
            model_name='notificationsettings',
            name='sms_notifications',
            field=models.BooleanField(verbose_name='Use sms for notifications', default=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(unique=True, verbose_name='email address', max_length=254),
        ),
        migrations.AlterField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', to='auth.Group', related_query_name='user', related_name='user_set', verbose_name='groups', blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_login',
            field=models.DateTimeField(verbose_name='last login', blank=True, null=True),
        ),
    ]
