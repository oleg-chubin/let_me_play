# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('let_me_app', '0019_court_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookingpolicy',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=8, verbose_name='estimated price'),
        ),
        migrations.AlterField(
            model_name='event',
            name='preliminary_price',
            field=models.DecimalField(decimal_places=2, max_digits=8, verbose_name='Preliminary price'),
        ),
    ]
