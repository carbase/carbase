# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-19 05:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('numberplates', '0003_auto_20170609_0502'),
    ]

    operations = [
        migrations.AddField(
            model_name='numberplate',
            name='is_installed',
            field=models.BooleanField(default=False),
        ),
    ]
