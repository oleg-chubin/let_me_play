# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def update_court_admin_group(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Court = apps.get_model("let_me_app", "Court")
    FollowerGroup = apps.get_model("let_me_auth", "FollowerGroup")
    courts = Court.objects.all()
    for court in courts:
        f_g = FollowerGroup(group_ptr=court.admin_group, followable=court)
        f_g.name = court.admin_group_id
        f_g.save()


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_app', '0018_galleryvideo'),
        ('auth', '0006_require_contenttypes_0002'),
        ('let_me_auth', '0007_auto_20160308_1347'),
    ]

    operations = [
        migrations.CreateModel(
            name='FollowerGroup',
            fields=[
                ('group_ptr', models.OneToOneField(to='auth.Group', parent_link=True, auto_created=True, primary_key=True, serialize=False)),
                ('followable', models.ForeignKey(to='let_me_app.Followable')),
            ],
            bases=('auth.group',),
        ),
        migrations.RunPython(update_court_admin_group),
    ]
