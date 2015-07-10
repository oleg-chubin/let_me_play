# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('comment', models.TextField(default='', max_length=256)),
                ('status', models.IntegerField(default=1, choices=[(1, 'Active'), (2, 'Accepted'), (3, 'Canceled'), (4, 'Declined')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BookingPolicy',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('early_registration', models.IntegerField(verbose_name='registration start within period')),
                ('price', models.IntegerField(verbose_name='estimated price')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Changelog',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date created')),
                ('text', models.TextField(verbose_name='text')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ChatParticipant',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('last_seen', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Followable',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('followable_ptr', models.OneToOneField(parent_link=True, primary_key=True, serialize=False, auto_created=True, to='let_me_app.Followable')),
                ('start_at', models.DateTimeField(verbose_name='date started')),
                ('name', models.CharField(default='', max_length=128)),
                ('description', models.TextField(default='', max_length=1024)),
                ('status', models.IntegerField(default=1, choices=[(1, 'Pending'), (2, 'Completed'), (3, 'Canceled')])),
            ],
            options={
            },
            bases=('let_me_app.followable',),
        ),
        migrations.CreateModel(
            name='Court',
            fields=[
                ('followable_ptr', models.OneToOneField(parent_link=True, primary_key=True, serialize=False, auto_created=True, to='let_me_app.Followable')),
                ('description', models.TextField(verbose_name='text')),
            ],
            options={
            },
            bases=('let_me_app.followable',),
        ),
        migrations.CreateModel(
            name='InternalMessage',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date created')),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('text', models.TextField(verbose_name='text')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('amount', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InventoryList',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('total_sum', models.DecimalField(decimal_places=2, max_digits=8)),
                ('status', models.IntegerField(default=1, choices=[(1, 'New'), (2, 'Paid'), (3, 'Not paid')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Occasion',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('start_at', models.DateTimeField(verbose_name='date started')),
                ('duration', models.IntegerField(verbose_name='duration (minutes)')),
                ('period', models.IntegerField(verbose_name='period (hours)')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Peeper',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PrivateComment',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date created')),
                ('text', models.TextField(verbose_name='text')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Proposal',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('comment', models.TextField(default='', max_length=256)),
                ('status', models.IntegerField(default=1, choices=[(1, 'Active'), (2, 'Accepted'), (3, 'Canceled'), (4, 'Declined')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Receipt',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('status', models.IntegerField(default=1, choices=[(1, 'New'), (2, 'Paid'), (3, 'Not paid')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('followable_ptr', models.OneToOneField(parent_link=True, primary_key=True, serialize=False, auto_created=True, to='let_me_app.Followable')),
                ('name', models.CharField(max_length=128)),
                ('description', models.TextField(verbose_name='text')),
                ('address', models.TextField(verbose_name='text')),
                ('map_image', models.ImageField(blank=True, null=True, upload_to='', verbose_name='map image')),
            ],
            options={
            },
            bases=('let_me_app.followable',),
        ),
        migrations.CreateModel(
            name='StaffProfile',
            fields=[
                ('followable_ptr', models.OneToOneField(parent_link=True, primary_key=True, serialize=False, auto_created=True, to='let_me_app.Followable')),
                ('description', models.TextField()),
            ],
            options={
            },
            bases=('let_me_app.followable',),
        ),
        migrations.CreateModel(
            name='Visit',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('status', models.IntegerField(default=1, choices=[(1, 'Pending'), (2, 'Completed'), (3, 'Canceled'), (4, 'Declined'), (5, 'Missed')])),
                ('event', models.ForeignKey(to='let_me_app.Event')),
                ('inventory_list', models.ForeignKey(null=True, blank=True, to='let_me_app.InventoryList')),
                ('receipt', models.ForeignKey(null=True, blank=True, to='let_me_app.Receipt')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
