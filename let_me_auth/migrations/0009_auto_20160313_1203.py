# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def create_anyone_group(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    FollowerGroup = apps.get_model("let_me_auth", "FollowerGroup")
    anyone_group, _ = FollowerGroup.objects.get_or_create(
        name="anyone", verbose_name="anyone")
    Event = apps.get_model("let_me_app", "Event")
    for event in Event.objects.all():
        anyone_group.targets.add(event)
    anyone_group.save()


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_app', '0018_galleryvideo'),
        ('let_me_auth', '0008_followergroup'),
    ]

    operations = [
        migrations.AddField(
            model_name='followergroup',
            name='targets',
            field=models.ManyToManyField(to='let_me_app.Followable', related_name='target_groups'),
        ),
        migrations.AddField(
            model_name='followergroup',
            name='verbose_name',
            field=models.CharField(verbose_name='verbose name', default='admin group', max_length=80),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='followergroup',
            name='followable',
            field=models.ForeignKey(null=True, related_name='group_owners', to='let_me_app.Followable'),
        ),
        migrations.RunPython(create_anyone_group),
    ]
