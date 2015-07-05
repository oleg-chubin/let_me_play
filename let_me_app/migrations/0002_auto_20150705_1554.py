# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_app', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='visit',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='staffprofile',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='proposal',
            name='event',
            field=models.ForeignKey(to='let_me_app.Event'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='proposal',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='privatecomment',
            name='followable',
            field=models.ForeignKey(related_name='users_comments', to='let_me_app.Followable'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='privatecomment',
            name='user',
            field=models.ForeignKey(related_name='my_comments', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='peeper',
            name='followable',
            field=models.ForeignKey(related_name='followers', to='let_me_app.Followable'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='peeper',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='occasion',
            name='equipment',
            field=models.ForeignKey(to='let_me_app.Court'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='inventory',
            name='equipment',
            field=models.ForeignKey(to='let_me_app.Equipment'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='inventory',
            name='inventory_list',
            field=models.ForeignKey(to='let_me_app.InventoryList'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='court',
            field=models.ForeignKey(to='let_me_app.Court'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='inventory_list',
            field=models.ForeignKey(null=True, blank=True, to='let_me_app.InventoryList'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='invoice',
            field=models.ForeignKey(null=True, blank=True, to='let_me_app.Invoice'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='staff',
            field=models.ManyToManyField(blank=True, to='let_me_app.StaffProfile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='court',
            name='admin_group',
            field=models.ForeignKey(to='auth.Group'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='court',
            name='site',
            field=models.ForeignKey(to='let_me_app.Site'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='chatparticipant',
            name='chat',
            field=models.ForeignKey(to='let_me_app.InternalMessage'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='chatparticipant',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='chatparticipant',
            unique_together=set([('user', 'chat')]),
        ),
        migrations.AddField(
            model_name='changelog',
            name='followable',
            field=models.ForeignKey(related_name='followable_set', to='let_me_app.Followable'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bookingpolicy',
            name='court',
            field=models.ForeignKey(to='let_me_app.Court'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bookingpolicy',
            name='group',
            field=models.ForeignKey(to='auth.Group'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='application',
            name='event',
            field=models.ForeignKey(to='let_me_app.Event'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='application',
            name='inventory_list',
            field=models.ForeignKey(null=True, blank=True, to='let_me_app.InventoryList'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='application',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
