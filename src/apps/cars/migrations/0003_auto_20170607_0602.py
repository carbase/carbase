# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-07 06:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0002_auto_20170607_0532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reregestration',
            name='inspection_time',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
