# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-12 07:13
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0013_agreement_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sign',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key_info', models.TextField()),
                ('signed_info', models.TextField()),
                ('signature_value', models.TextField()),
            ],
        ),
        migrations.RenameField(
            model_name='agreement',
            old_name='template_html',
            new_name='template',
        ),
        migrations.RemoveField(
            model_name='agreement',
            name='style',
        ),
        migrations.RemoveField(
            model_name='agreement',
            name='template_pdf',
        ),
        migrations.RemoveField(
            model_name='agreement',
            name='template_xml',
        ),
        migrations.RemoveField(
            model_name='agreement',
            name='title',
        ),
        migrations.AddField(
            model_name='agreement',
            name='context',
            field=django.contrib.postgres.fields.jsonb.JSONField(default={}),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='agreement',
            name='owner',
            field=models.TextField(),
        ),
        migrations.AddField(
            model_name='sign',
            name='agreement',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cars.Agreement'),
        ),
    ]