# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from django.db import models, migrations
from django.core.files import File


def combine_names(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    ActivityType = apps.get_model("let_me_app", "ActivityType")
    file_name = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'static/images/volley_logo.gif'
    )
    activity_type = ActivityType(title='Default')
    activity_type.image.save('logo.gif', File(open(file_name, 'rb')))
    activity_type.save()

class Migration(migrations.Migration):

    dependencies = [
        ('let_me_app', '0006_internalmessage_subject'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityType',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='', verbose_name='image')),
                ('title', models.CharField(max_length=128)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RunPython(combine_names),
        migrations.AddField(
            model_name='court',
            name='activity_type',
            field=models.ForeignKey(default=1, to='let_me_app.ActivityType'),
            preserve_default=False,
        ),
    ]
