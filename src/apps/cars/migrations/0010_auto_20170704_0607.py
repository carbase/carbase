# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-04 06:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0009_deregistration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='number',
            field=models.CharField(blank=True, default='', max_length=16),
        ),
    ]