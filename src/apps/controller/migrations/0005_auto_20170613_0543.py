# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-13 05:43
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('controller', '0004_auto_20170609_0640'),
    ]

    operations = [
        migrations.RenameField(
            model_name='inspection',
            old_name='reregestration',
            new_name='reregistration',
        ),
    ]