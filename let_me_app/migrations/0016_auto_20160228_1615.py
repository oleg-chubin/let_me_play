# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('let_me_app', '0015_auto_20160220_1338'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoolnessRate',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('value', models.IntegerField(choices=[(1, 'weaker'), (2, 'bit_weaker'), (3, 'same'), (4, 'bit_stronger'), (4, 'stronger')], default=3)),
                ('rater', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('topic', models.ForeignKey(related_name='expertise', to='let_me_app.Followable')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='coolnessrate',
            unique_together=set([('topic', 'rater')]),
        ),
    ]
