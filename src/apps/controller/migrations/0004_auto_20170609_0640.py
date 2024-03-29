# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-09 06:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('controller', '0003_auto_20170609_0637'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inspection',
            name='center',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='controller.Center'),
        ),
        migrations.AlterField(
            model_name='inspection',
            name='date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='inspection',
            name='is_success',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='inspection',
            name='time_range',
            field=models.CharField(max_length=11, null=True),
        ),
    ]
