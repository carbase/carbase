# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-22 06:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0006_reregistration_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('iin', models.CharField(max_length=12)),
                ('email', models.CharField(max_length=256)),
            ],
        ),
    ]
