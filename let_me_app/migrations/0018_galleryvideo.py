# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import embed_video.fields


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_app', '0017_auto_20160308_1347'),
    ]

    operations = [
        migrations.CreateModel(
            name='GalleryVideo',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('video', embed_video.fields.EmbedVideoField()),
                ('note', models.CharField(verbose_name='note', max_length=128, default='just a picture')),
                ('followable', models.ForeignKey(to='let_me_app.Followable')),
            ],
        ),
    ]
