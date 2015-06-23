# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('let_me_app', '0002_auto_20150222_1502'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatParticipant',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('chat', models.ForeignKey(to='let_me_app.InternalMessage')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='chatparticipant',
            unique_together=set([('user', 'chat')]),
        ),
        migrations.RemoveField(
            model_name='internalmessage',
            name='recipient',
        ),
        migrations.RemoveField(
            model_name='internalmessage',
            name='sender',
        ),
        migrations.AddField(
            model_name='internalmessage',
            name='last_update',
            field=models.DateTimeField(default=datetime.datetime(2015, 5, 31, 14, 16, 5, 319386, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
