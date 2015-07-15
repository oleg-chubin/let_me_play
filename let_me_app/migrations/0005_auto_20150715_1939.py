# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_app', '0004_auto_20150713_2126'),
    ]

    operations = [
        migrations.CreateModel(
            name='GalleryImage',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('image', models.ImageField(verbose_name='image', upload_to='')),
                ('thumbnail', models.ImageField(null=True, verbose_name='thumbnail', blank=True, upload_to='')),
                ('note', models.CharField(default='just a picture', max_length=128)),
                ('followable', models.ForeignKey(to='let_me_app.Followable')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='site',
            name='map_image',
        ),
    ]
