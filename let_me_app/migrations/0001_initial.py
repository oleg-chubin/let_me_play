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
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('comment', models.TextField(max_length=256, default='')),
                ('status', models.IntegerField(choices=[(1, 'Active'), (2, 'Accepted'), (3, 'Canceled'), (4, 'Declined')], default=1)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BookingPolicy',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('early_registration', models.IntegerField(verbose_name='registration start within period')),
                ('price', models.IntegerField(verbose_name='estimated price')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=256)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Followable',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('followable_ptr', models.OneToOneField(serialize=False, to='let_me_app.Followable', auto_created=True, primary_key=True, parent_link=True)),
                ('start_at', models.DateTimeField(verbose_name='date started')),
                ('name', models.CharField(max_length=128, default='')),
                ('description', models.TextField(max_length=1024, default='')),
            ],
            options={
            },
            bases=('let_me_app.followable',),
        ),
        migrations.CreateModel(
            name='Court',
            fields=[
                ('followable_ptr', models.OneToOneField(serialize=False, to='let_me_app.Followable', auto_created=True, primary_key=True, parent_link=True)),
                ('description', models.TextField(verbose_name='text')),
                ('admin_group', models.ForeignKey(to='auth.Group')),
            ],
            options={
            },
            bases=('let_me_app.followable',),
        ),
        migrations.CreateModel(
            name='Changelog',
            fields=[
                ('followable_ptr', models.OneToOneField(serialize=False, to='let_me_app.Followable', auto_created=True, primary_key=True, parent_link=True)),
                ('created_at', models.DateTimeField(verbose_name='date created', default=django.utils.timezone.now)),
                ('text', models.TextField(verbose_name='text')),
            ],
            options={
            },
            bases=('let_me_app.followable',),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('followable_ptr', models.OneToOneField(serialize=False, to='let_me_app.Followable', auto_created=True, primary_key=True, parent_link=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(verbose_name='last login', default=django.utils.timezone.now)),
                ('is_superuser', models.BooleanField(verbose_name='superuser status', default=False, help_text='Designates that this user has all permissions without explicitly assigning them.')),
                ('email', models.EmailField(unique=True, max_length=75, verbose_name='email address')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('is_staff', models.BooleanField(verbose_name='staff status', default=False, help_text='Designates whether the user can log into this admin site.')),
                ('is_active', models.BooleanField(verbose_name='active', default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')),
                ('date_joined', models.DateTimeField(verbose_name='date joined', default=django.utils.timezone.now)),
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
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='date created', default=django.utils.timezone.now)),
                ('text', models.TextField(verbose_name='text')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
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
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=256)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=128)),
                ('total_sum', models.DecimalField(max_digits=8, decimal_places=2)),
                ('status', models.IntegerField(choices=[(1, 'New'), (2, 'Paid'), (3, 'Not paid')], default=1)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Occasion',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('start_at', models.DateTimeField(verbose_name='date started')),
                ('duration', models.IntegerField(verbose_name='duration (minutes)')),
                ('period', models.IntegerField(verbose_name='period (hours)')),
                ('equipment', models.ForeignKey(to='let_me_app.Court')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Peeper',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PrivateComment',
            fields=[
                ('followable_ptr', models.OneToOneField(serialize=False, to='let_me_app.Followable', auto_created=True, primary_key=True, parent_link=True)),
                ('created_at', models.DateTimeField(verbose_name='date created', default=django.utils.timezone.now)),
                ('text', models.TextField(verbose_name='text')),
            ],
            options={
            },
            bases=('let_me_app.followable',),
        ),
        migrations.CreateModel(
            name='Proposal',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('comment', models.TextField(max_length=256, default='')),
                ('status', models.IntegerField(choices=[(1, 'Active'), (2, 'Accepted'), (3, 'Canceled'), (4, 'Declined')], default=1)),
                ('event', models.ForeignKey(to='let_me_app.Event')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Receipt',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('price', models.DecimalField(max_digits=8, decimal_places=2)),
                ('status', models.IntegerField(choices=[(1, 'New'), (2, 'Paid'), (3, 'Not paid')], default=1)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('followable_ptr', models.OneToOneField(serialize=False, to='let_me_app.Followable', auto_created=True, primary_key=True, parent_link=True)),
                ('name', models.CharField(max_length=128)),
                ('description', models.TextField(verbose_name='text')),
                ('address', models.TextField(verbose_name='text')),
                ('map_image', models.ImageField(null=True, upload_to='', blank=True, verbose_name='map image')),
            ],
            options={
            },
            bases=('let_me_app.followable',),
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('user_ptr', models.OneToOneField(serialize=False, to=settings.AUTH_USER_MODEL, auto_created=True, primary_key=True, parent_link=True)),
                ('description', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('let_me_app.user',),
        ),
        migrations.CreateModel(
            name='Visit',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('event', models.ForeignKey(to='let_me_app.Event')),
                ('inventory_list', models.ForeignKey(blank=True, to='let_me_app.InventoryList', null=True)),
                ('receipt', models.ForeignKey(blank=True, to='let_me_app.Receipt', null=True)),
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
            model_name='inventory',
            name='inventory_list',
            field=models.ForeignKey(to='let_me_app.InventoryList'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='internalmessage',
            name='recipient',
            field=models.ForeignKey(related_name='incoming_messages', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='internalmessage',
            name='sender',
            field=models.ForeignKey(related_name='outgoing_messages', to=settings.AUTH_USER_MODEL),
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
            field=models.ForeignKey(blank=True, to='let_me_app.InventoryList', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='invoice',
            field=models.ForeignKey(blank=True, to='let_me_app.Invoice', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='staff',
            field=models.ManyToManyField(to='let_me_app.Staff'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='court',
            name='site',
            field=models.ForeignKey(to='let_me_app.Site'),
            preserve_default=True,
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
            field=models.ForeignKey(blank=True, to='let_me_app.InventoryList', null=True),
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
            field=models.ManyToManyField(related_name='user_set', blank=True, verbose_name='groups', help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', to='auth.Group', related_query_name='user'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(related_name='user_set', blank=True, verbose_name='user permissions', help_text='Specific permissions for this user.', to='auth.Permission', related_query_name='user'),
            preserve_default=True,
        ),
    ]
