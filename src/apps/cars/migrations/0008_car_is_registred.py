# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-28 07:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0007_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='is_registred',
            field=models.BooleanField(default=True),
        ),
    ]
