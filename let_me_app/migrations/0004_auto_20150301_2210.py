# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_app', '0003_internalmessage_state'),
    ]

    operations = [
        migrations.CreateModel(
            name='GalleryImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('image', models.ImageField(verbose_name='image', upload_to='images')),
                ('followable', models.ForeignKey(to='let_me_app.Followable')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='site',
            name='address',
            field=models.TextField(verbose_name='address'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='site',
            name='description',
            field=models.TextField(verbose_name='description'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='site',
            name='map_image',
            field=models.ImageField(blank=True, verbose_name='map image', upload_to='map_images', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='site',
            name='name',
            field=models.CharField(verbose_name='name', max_length=128),
            preserve_default=True,
        ),
    ]
