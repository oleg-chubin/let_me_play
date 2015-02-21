# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Followable',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('followable_ptr', models.OneToOneField(parent_link=True, to='let_me_app.Followable', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('description', models.TextField(max_length=1024)),
            ],
            options={
            },
            bases=('let_me_app.followable',),
        ),
        migrations.CreateModel(
            name='Court',
            fields=[
                ('followable_ptr', models.OneToOneField(parent_link=True, to='let_me_app.Followable', auto_created=True, serialize=False, primary_key=True)),
                ('group', models.ForeignKey(to='auth.Group')),
            ],
            options={
            },
            bases=('let_me_app.followable',),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('followable_ptr', models.OneToOneField(parent_link=True, to='let_me_app.Followable', auto_created=True, serialize=False, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=75, verbose_name='email address', unique=True)),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=('let_me_app.followable', models.Model),
        ),
        migrations.CreateModel(
            name='InternalMessage',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('amount', models.IntegerField()),
                ('equipment', models.ForeignKey(to='let_me_app.Equipment')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InventoryList',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('quantity', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Peeper',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PrivateComment',
            fields=[
                ('followable_ptr', models.OneToOneField(parent_link=True, to='let_me_app.Followable', auto_created=True, serialize=False, primary_key=True)),
            ],
            options={
            },
            bases=('let_me_app.followable',),
        ),
        migrations.CreateModel(
            name='Proposal',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('description', models.TextField(max_length=1024)),
                ('event', models.ForeignKey(to='let_me_app.Event')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Receipt',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('price', models.DecimalField(max_digits=8, decimal_places=2)),
                ('status', models.IntegerField(default=1, choices=[(1, 'New'), (2, 'Approved'), (3, 'Rejected'), (4, 'Paid'), (5, 'Not paid')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('followable_ptr', models.OneToOneField(parent_link=True, to='let_me_app.Followable', auto_created=True, serialize=False, primary_key=True)),
            ],
            options={
            },
            bases=('let_me_app.followable',),
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('user_ptr', models.OneToOneField(parent_link=True, to=settings.AUTH_USER_MODEL, auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('event', models.ForeignKey(to='let_me_app.Event')),
            ],
            options={
                'abstract': False,
            },
            bases=('let_me_app.user',),
        ),
        migrations.CreateModel(
            name='Visit',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('event', models.ForeignKey(to='let_me_app.Event')),
                ('inventory_list', models.ForeignKey(to='let_me_app.InventoryList')),
                ('receipet', models.ForeignKey(to='let_me_app.Receipt')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='proposal',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='privatecomment',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='peeper',
            name='followable',
            field=models.ForeignKey(to='let_me_app.Followable', related_name='followers'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='peeper',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='inventory',
            name='inventory_list',
            field=models.ForeignKey(to='let_me_app.InventoryList'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='internalmessage',
            name='recipient',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='recipient'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='internalmessage',
            name='sender',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='sender'),
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
            field=models.ForeignKey(to='let_me_app.InventoryList'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='invoice',
            field=models.ForeignKey(to='let_me_app.Invoice'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='court',
            name='site',
            field=models.ForeignKey(to='let_me_app.Site'),
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
            field=models.ForeignKey(to='let_me_app.InventoryList'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='application',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(to='auth.Group', related_query_name='user', related_name='user_set', help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', blank=True, verbose_name='groups'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(to='auth.Permission', related_query_name='user', related_name='user_set', help_text='Specific permissions for this user.', blank=True, verbose_name='user permissions'),
            preserve_default=True,
        ),
    ]
