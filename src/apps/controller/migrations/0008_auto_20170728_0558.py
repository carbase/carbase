# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-28 05:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('controller', '0007_auto_20170724_0557'),
    ]

    operations = [
        migrations.AddField(
            model_name='inspection',
            name='prelimenary_sign',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='inspection',
            name='revision_sign',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='inspection',
            name='sign',
            field=models.TextField(blank=True, null=True),
        ),
    ]
